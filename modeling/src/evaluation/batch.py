
"""Sequential and resumable LLM batch generation."""

import fcntl
import hashlib
import json
import os
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


class BatchGenerator:
    """Process prompts sequentially with persistence and memory protection."""

    MEMORY_ERRORS = (
        "out of memory",
        "not enough memory",
        "insufficient memory",
        "cannot allocate memory",
        "failed to allocate",
        "cuda error: out of memory",
    )

    def __init__(self, generator, run_dir, memory_guard=None, max_attempts=2):
        if type(max_attempts) is not int or max_attempts < 1:
            raise ValueError("max_attempts must be a positive integer")

        self.generator = generator
        self.run_dir = Path(run_dir)
        self.memory_guard = memory_guard
        self.max_attempts = max_attempts

    @staticmethod
    def _prompt_id(text: str) -> str:
        """Create a stable identifier from normalized prompt text."""
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    @staticmethod
    def _sync(stream) -> None:
        """Flush buffered data to disk."""
        stream.flush()
        os.fsync(stream.fileno())

    def _validate_config(self) -> None:
        """Ensure the run uses a consistent inference configuration."""
        path = self.run_dir / "config.json"
        config = self.generator.config.to_dict()

        if path.exists():
            manifest = json.loads(path.read_text(encoding="utf-8"))

            if manifest["config"] != config:
                raise ValueError("Run configuration changed: use a new directory")
            return

        manifest = {
            "config": config,
            "created_at": datetime.now(UTC).isoformat(),
        }

        temporary = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.run_dir,
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary = Path(stream.name)
                json.dump(manifest, stream, ensure_ascii=False, indent=2)
                self._sync(stream)

            temporary.replace(path)

        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    @staticmethod
    def _validate_history_record(record: dict) -> None:
        """Validate the required fields of a persisted attempt."""
        if (
            not isinstance(record.get("prompt_id"), str)
            or not record["prompt_id"]
            or type(record.get("attempt")) is not int
            or record["attempt"] < 1
            or not isinstance(record.get("status"), str)
        ):
            raise ValueError("Invalid history record")

    def _repair_tail(self, stream, position: int) -> None:
        """Remove only a truncated final JSONL record."""
        stream.truncate(position)
        self._sync(stream)

    def _read_history_records(self, path: Path):
        """Read valid records and recover an interrupted final write."""
        if not path.exists():
            return

        with path.open("r+b") as stream:
            line_number = 0

            while True:
                position = stream.tell()
                line = stream.readline()

                if not line:
                    break

                line_number += 1

                if not line.strip():
                    if not line.endswith(b"\n"):
                        self._repair_tail(stream, position)
                        break
                    continue

                try:
                    record = json.loads(line)

                    if not isinstance(record, dict):
                        raise ValueError("Expected JSON object")

                    self._validate_history_record(record)

                except (ValueError, UnicodeDecodeError) as error:
                    if not line.endswith(b"\n"):
                        self._repair_tail(stream, position)
                        break

                    raise ValueError(
                        f"Corrupted JSONL record at {path}:{line_number}"
                    ) from error

                if not line.endswith(b"\n"):
                    stream.seek(0, os.SEEK_END)
                    stream.write(b"\n")
                    self._sync(stream)

                yield record

    @staticmethod
    def _is_complete(record: dict) -> bool:
        """Check whether Ollama returned a completed, nonempty response."""
        response = record.get("response")

        return (
            record.get("status") == "generated"
            and isinstance(response, str)
            and bool(response.strip())
            and record.get("done") is not False
            and record.get("done_reason") != "length"
        )

    def _is_memory_error(self, record: dict) -> bool:
        """Identify a reported out-of-memory generation error."""
        if record.get("status") != "generation_error":
            return False

        error = str(record.get("error", "")).lower()
        return any(message in error for message in self.MEMORY_ERRORS)

    def _memory_pressure(self, record: dict) -> bool:
        """Detect reported memory errors or critically low available RAM."""
        if self._is_memory_error(record):
            return True

        if self.memory_guard is None:
            return False

        minimum_ram = record.get("memory", {}).get("min_ram_available_gib")

        return (
            minimum_ram is not None
            and minimum_ram < self.memory_guard.min_ram_gib
        )

    def _load_history(self):
        """Recover attempt numbers, technical failures, and completed prompts."""
        attempts = Counter()
        failures = Counter()
        completed = set()

        path = self.run_dir / "responses.jsonl"

        for record in self._read_history_records(path):
            identifier = record["prompt_id"]

            if record["attempt"] <= attempts[identifier]:
                raise ValueError(f"Duplicate or unordered attempt: {identifier}")

            attempts[identifier] = record["attempt"]

            if self._is_complete(record):
                completed.add(identifier)
            elif not self._is_memory_error(record):
                failures[identifier] += 1

        return attempts, failures, completed

    def _call_generator(self, text: str, attempt: int) -> dict:
        """Execute one inference and capture technical failures."""
        try:
            return self.generator.generate(text, attempt=attempt)

        except Exception as error:
            return {
                "prompt": text,
                "status": "generation_error",
                "error": str(error),
            }

    def _generate(self, text: str, attempt: int) -> dict:
        """Collect memory measurements around one inference."""
        guard = self.memory_guard

        if guard is None:
            return self._call_generator(text, attempt)

        with guard.observe() as samples:
            record = self._call_generator(text, attempt)

        record["memory"] = guard.summarize(samples)
        return record

    def _prepare_record(
        self, record: dict, identifier: str, attempt: int
    ) -> dict:
        """Normalize the generation status and attach attempt metadata."""
        if record.get("status") == "generated" and not self._is_complete(record):
            record["status"] = "incomplete_generation"

        if record.get("status") not in {
            "generated",
            "generation_error",
            "incomplete_generation",
        }:
            raise ValueError("Invalid generator response status")

        record.update(
            schema_version=1,
            prompt_id=identifier,
            attempt=attempt,
            response_id=f"{self.run_dir.name}:{identifier}:{attempt}",
            created_at=datetime.now(UTC).isoformat(),
        )

        if self._memory_pressure(record):
            record["memory_warning"] = True

        return record

    def _save_record(self, record: dict) -> None:
        """Persist a complete attempt before processing another prompt."""
        path = self.run_dir / "responses.jsonl"
        data = (json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8")

        with path.open("ab") as stream:
            stream.write(data)
            self._sync(stream)

    def _parse_prompt(self, prompt) -> tuple[str, str]:
        """Validate a prompt and resolve its stable identifier."""
        if isinstance(prompt, str):
            text = prompt
            supplied_id = None
        elif isinstance(prompt, dict):
            text = prompt.get("prompt")
            supplied_id = prompt.get("prompt_id")
        else:
            raise TypeError("Expected a string or prompt dictionary")

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Prompt must be non-empty text")

        identifier = self._prompt_id(text)

        if supplied_id is not None and supplied_id != identifier:
            raise ValueError("prompt_id does not match prompt text")

        return text, identifier

    def _process_prompt(
        self, text, identifier, attempts, failures, completed, counts
    ) -> str | None:
        """Process one prompt until completion, pause, or retry limit."""
        while failures[identifier] < self.max_attempts:
            if self.memory_guard is not None:
                if not self.memory_guard.can_start():
                    return "Insufficient available RAM"

            attempt = attempts[identifier] + 1
            record = self._generate(text, attempt)
            record = self._prepare_record(record, identifier, attempt)

            self._save_record(record)

            attempts[identifier] = attempt
            counts[record["status"]] += 1

            if self._is_complete(record):
                completed.add(identifier)

            elif not self._is_memory_error(record):
                failures[identifier] += 1

            if self._memory_pressure(record):
                return "Memory pressure or out-of-memory error"

            if identifier in completed:
                return None

        counts["blocked"] += 1
        return None

    def _run_locked(self, prompts):
        """Coordinate sequential processing and experiment recovery."""
        self._validate_config()

        attempts, failures, completed = self._load_history()

        counts = Counter(
            generated=0,
            generation_error=0,
            incomplete_generation=0,
            skipped=0,
            blocked=0,
        )

        paused_reason = None

        for prompt in prompts:
            text, identifier = self._parse_prompt(prompt)

            if identifier in completed:
                counts["skipped"] += 1
                continue

            paused_reason = self._process_prompt(
                text, identifier, attempts, failures, completed, counts
            )

            if paused_reason is not None:
                break

        return {
            **counts,
            "paused_reason": paused_reason,
            "responses_path": str(self.run_dir / "responses.jsonl"),
        }

    def run(self, prompts):
        """Execute the batch under an exclusive file lock."""
        self.run_dir.mkdir(parents=True, exist_ok=True)

        with (self.run_dir / ".writer.lock").open("a") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError("This run already has an active writer") from error

            try:
                return self._run_locked(prompts)
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
