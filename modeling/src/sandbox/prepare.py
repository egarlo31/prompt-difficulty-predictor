"""Prepare auditable sandbox task records without executing generated code."""
from collections import Counter
import json
from pathlib import Path
import re
import tempfile

from modeling.src.data.prompt_io import read_jsonl
from modeling.src.sandbox.contracts import SandboxLimits


def extract_python(response):
    """Accept one explicit Python fence; ambiguous/unfenced responses need review."""
    if not isinstance(response, str):
        return None
    blocks = re.findall(r"^```([^\n]*)\n(.*?)^```[ \t]*$", response, re.MULTILINE | re.DOTALL)
    if len(blocks) != 1 or blocks[0][0].strip().lower() not in {"python", "python3", "py"}:
        return None
    return blocks[0][1].strip() or None


def prepare_sandbox_tasks(responses_path, tasks_path, *, limits=None):
    """Export tasks pending reviewed code and TACO test specifications.

    Test specs must later join by prompt_id to raw TACO provenance (split,
    index). Embedded examples are not a replacement for ground-truth tests.
    """
    responses_path, tasks_path = Path(responses_path), Path(tasks_path)
    if responses_path.resolve() == tasks_path.resolve():
        raise ValueError("Tasks must not overwrite responses")
    limits = limits or SandboxLimits()
    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=tasks_path.parent,
                                         delete=False, suffix=".tmp") as stream:
            temporary = Path(stream.name)
            for record in read_jsonl(responses_path):
                if record["status"] != "generated":
                    counts["skipped_generation_error"] += 1
                    continue
                code = extract_python(record.get("response"))
                status = "pending_test_spec" if code else "needs_code_review"
                # Interactive problems need a live judge, not ordinary stdin tests.
                if re.search(r"\binteractive problem\b", record.get("prompt", ""), re.IGNORECASE):
                    status = "requires_interactive_judge"
                if record.get("done") is False or record.get("done_reason") == "length":
                    status = "incomplete_generation"
                task = {
                    "schema_version": 1, "task_id": record["response_id"],
                    "prompt_id": record["prompt_id"], "response_id": record["response_id"],
                    "language": "python", "code": code, "test_spec": None,
                    "limits": limits.to_dict(), "status": status,
                }
                stream.write(json.dumps(task, ensure_ascii=False) + "\n")
                counts[status] += 1
        temporary.replace(tasks_path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {**counts, "tasks_path": str(tasks_path)}
