"""Validated, lazy prompt loading shared by notebooks and batch inference."""
import hashlib
import json
from pathlib import Path


def prompt_id(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON at {path}:{line_number}") from error
            if not isinstance(row, dict):
                raise ValueError(f"Expected object at {path}:{line_number}")
            yield row


def load_prompts(path, *, limit=None):
    """Yield {prompt_id, prompt} without loading the full dataset in memory."""
    if limit is not None and limit < 1:
        raise ValueError("limit must be positive or None")
    from itertools import islice
    for row in islice(read_jsonl(path), limit):
        text = row.get("prompt")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Invalid prompt in {path}")
        yield {"prompt_id": prompt_id(text), "prompt": text}
