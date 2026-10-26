"""Incremental and resumable JSONL inference through EvaluationRunner."""
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from modeling.src.data.prompt_io import prompt_id, read_jsonl

CODING_SYSTEM = (
    "Solve the programming problem in Python 3. Return exactly one fenced "
    "python code block containing the complete solution, without explanations. "
    "Follow the input/output format and function signature in the statement. "
    "Do not access files, the network or external services."
)


def generate_batch(prompts, evaluator, run_dir):
    """Save each attempt immediately; resume successes and retry failures.

    A run directory belongs to one configuration and one writer. Reuse it to
    resume that configuration; use a new directory to change model or options.
    Malformed/truncated JSONL is reported rather than silently discarded.
    """
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    adapter = evaluator.adapter
    config = {
        "schema_version": 1, "model": adapter.model, "host": adapter.host,
        "options": dict(adapter.options), "system": adapter.system,
        "think": adapter.think, "keep_alive": adapter.keep_alive,
    }
    manifest_path = run_dir / "config.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["config"] != config:
            raise ValueError("Run configuration changed: choose a new run directory")
    else:
        manifest = {"config": config, "created_at": datetime.now(timezone.utc).isoformat()}
        with manifest_path.open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, ensure_ascii=False, indent=2)

    output_path = run_dir / "responses.jsonl"
    attempts, completed = Counter(), set()
    if output_path.exists():
        for record in read_jsonl(output_path):
            identifier = record["prompt_id"]
            attempts[identifier] = max(attempts[identifier], record["attempt"])
            if record["status"] == "generated":
                completed.add(identifier)

    counts = Counter(generated=0, generation_error=0, skipped=0)
    with output_path.open("a", encoding="utf-8") as stream:
        for prompt in prompts:
            text = prompt["prompt"]
            identifier = prompt_id(text)
            if prompt["prompt_id"] != identifier:
                raise ValueError("prompt_id does not match prompt text")
            if identifier in completed:
                counts["skipped"] += 1
                continue
            record = evaluator.evaluate(text)
            attempts[identifier] += 1
            record.update(
                schema_version=1, prompt_id=identifier, attempt=attempts[identifier],
                response_id=f"{run_dir.name}:{identifier}:{attempts[identifier]}",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
            counts[record["status"]] += 1
            if record["status"] == "generated":
                completed.add(identifier)
    return {**counts, "responses_path": str(output_path)}
