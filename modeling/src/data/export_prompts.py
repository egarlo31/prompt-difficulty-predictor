
"""TACO dataset validation and prompt export utilities."""

import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Iterable

import pandas as pd

from modeling.src.data.taco_dataset import TacoArrowDataset


MODELING_DIR = Path(__file__).resolve().parents[2]


class DatasetManager:
    """Manage TACO dataset candidates and project paths."""

    def __init__(self, data_dir: Path | str | None = None) -> None:
        """Initialize the dataset directory, defaulting to modeling/data."""
        self.data_dir = Path(data_dir) if data_dir is not None else MODELING_DIR / "data"

    def load_candidates(self) -> pd.DataFrame:
        """Load and validate candidate identifiers from CSV."""
        path = self.data_dir / "interim" / "candidate_ids.csv"
        return self._validate_candidates(pd.read_csv(path))

    @staticmethod
    def _validate_candidates(df: pd.DataFrame) -> pd.DataFrame:
        """Validate candidate indices, dataset splits, and uniqueness.

        Returns:
            A validated DataFrame with integer indices.

        Raises:
            ValueError: If candidate identifiers are invalid or duplicated.
        """
        missing = {"split", "idx"} - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        df = df.copy()

        if df[["split", "idx"]].isna().any().any():
            raise ValueError("Missing candidate identifiers")

        numeric = pd.to_numeric(df["idx"], errors="coerce")
        if numeric.isna().any() or (numeric % 1 != 0).any():
            raise ValueError("Candidate indices must be integers")

        try:
            df["idx"] = numeric.astype("int64")
        except (ValueError, TypeError) as exc:
            raise ValueError("Invalid candidate indices") from exc

        if (df["idx"] < 0).any():
            raise ValueError("Invalid candidate indices: negative values found")

        if not df["split"].isin({"train", "test"}).all():
            raise ValueError("Invalid dataset split")

        if df.duplicated(subset=["split", "idx"]).any():
            raise ValueError("Duplicate candidates")

        return df

    @staticmethod
    def configure_imports() -> None:
        """Locate the project root and add it to sys.path.

        Raises:
            FileNotFoundError: If the modeling/src directory is not found.
        """
        current = Path.cwd()

        for parent in (current, *current.parents):
            if (parent / "modeling" / "src").is_dir():
                root = str(parent)
                if root not in sys.path:
                    sys.path.insert(0, root)
                return

        raise FileNotFoundError("Project root containing 'modeling/src' not found")


class PromptOperation(DatasetManager):
    """Extract, validate, deduplicate, and export TACO prompts."""

    @staticmethod
    def _validate_prompts(questions: Iterable[str | None], min_chars: int, counts: Counter):
        """Yield valid prompts alongside their whitespace-normalized text."""
        for question in questions:
            counts["read"] += 1

            if question is None:
                counts["empty_or_short"] += 1
                continue

            if not isinstance(question, str):
                raise ValueError("Expected question to be text or null")

            normalized = question.strip()

            if len(normalized) < min_chars:
                counts["empty_or_short"] += 1
                continue

            yield question, normalized

    @staticmethod
    def _deduplicate_prompts(prompts: Iterable[tuple[str, str]], counts: Counter):
        """Yield unique prompts using SHA-256 hashes of normalized text."""
        seen: set[bytes] = set()

        for question, normalized in prompts:
            digest = hashlib.sha256(normalized.encode("utf-8")).digest()

            if digest in seen:
                counts["duplicates"] += 1
                continue

            seen.add(digest)
            yield question

    @staticmethod
    def _write_jsonl(prompts: Iterable[str], destination: Path) -> int:
        """Atomically write prompts to JSONL and return the exported count."""
        destination.parent.mkdir(parents=True, exist_ok=True)

        temporary = None
        exported = 0

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=destination.parent,
                suffix=".tmp",
                delete=False,
            ) as output:
                temporary = Path(output.name)

                for prompt in prompts:
                    output.write(json.dumps({"prompt": prompt}, ensure_ascii=False) + "\n")
                    exported += 1

            temporary.replace(destination)

        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

        return exported

    def export_prompts(
        self,
        questions: Iterable[str | None],
        destination: Path | str,
        min_chars: int = 1,
        deduplicate: bool = True,
    ) -> dict[str, int]:
        """Validate, optionally deduplicate, and export prompts to JSONL.

        Args:
            questions: Input prompt collection.
            destination: Output JSONL file path.
            min_chars: Minimum prompt length after stripping whitespace.
            deduplicate: Whether to remove repeated normalized prompts.

        Returns:
            Counts for read, exported, empty_or_short, and duplicates.
        """
        if min_chars < 1:
            raise ValueError("min_chars must be positive")

        counts = Counter(read=0, exported=0, empty_or_short=0, duplicates=0)
        valid = self._validate_prompts(questions, min_chars, counts)

        prompts = (
            self._deduplicate_prompts(valid, counts)
            if deduplicate
            else (question for question, _ in valid)
        )

        counts["exported"] = self._write_jsonl(prompts, Path(destination))

        return dict(counts)

    def extract_and_export_prompts(
        self,
        raw_dir: Path | str | None = None,
        destination: Path | str | None = None,
        split: str = "all",
        min_chars: int = 1,
        deduplicate: bool = True,
    ) -> dict[str, int]:
        """Extract prompts from TACO Arrow shards and export them to JSONL.

        Args:
            raw_dir: Source directory, defaulting to data/raw/TACO.
            destination: Output file, defaulting to data/processed/prompts.jsonl.
            split: Dataset partition ('train', 'test', or 'all').
            min_chars: Minimum valid prompt length.
            deduplicate: Whether to exclude duplicate prompts.

        Returns:
            Prompt validation and export statistics.
        """
        raw_path = Path(raw_dir).resolve() if raw_dir else (self.data_dir / "raw" / "TACO").resolve()
        dest_path = Path(destination) if destination else self.data_dir / "processed" / "prompts.jsonl"
        splits = ["train", "test"] if split == "all" else [split]

        questions = TacoArrowDataset(raw_path).questions(splits)
        return self.export_prompts(questions, dest_path, min_chars, deduplicate)
