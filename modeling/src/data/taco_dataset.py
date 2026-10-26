
"""Download and read version-pinned TACO Arrow datasets."""

import json
from datetime import UTC, datetime
from pathlib import Path
from collections.abc import Iterator

from huggingface_hub import HfApi, snapshot_download


MODELING_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = MODELING_DIR / "data" / "raw" / "TACO"
MANIFEST = MODELING_DIR / "results" / "taco_manifest.json"


class TacoDataset:
    """Manage TACO dataset downloads and read-only Arrow access."""

    REPO_ID = "BAAI/TACO"

    def __init__(self, raw_dir: Path | str = RAW_DIR, manifest_path: Path | str = MANIFEST):
        self.raw_dir = Path(raw_dir)
        self.manifest_path = Path(manifest_path)

    def download(self, revision: str | None = None) -> str:
        """Download Arrow shards and record the dataset revision."""
        if revision is None and self.manifest_path.exists():
            revision = json.loads(self.manifest_path.read_text(encoding="utf-8"))["revision"]

        sha = HfApi().dataset_info(self.REPO_ID, revision=revision).sha

        if sha is None:
            raise RuntimeError(f"Could not resolve dataset revision for {self.REPO_ID}")

        if self.manifest_path.exists() and list(self.raw_dir.glob("*/*.arrow")):
            previous = json.loads(self.manifest_path.read_text(encoding="utf-8"))["revision"]

            if previous != sha:
                raise ValueError("Use a separate directory for a different dataset revision")

        self.raw_dir.mkdir(parents=True, exist_ok=True)

        snapshot_download(
            repo_id=self.REPO_ID,
            repo_type="dataset",
            revision=sha,
            local_dir=self.raw_dir,
            allow_patterns=["train/*.arrow", "test/*.arrow", "README.md"],
        )

        files = {
            path.relative_to(self.raw_dir).as_posix(): path.stat().st_size
            for path in sorted(self.raw_dir.glob("*/*.arrow"))
        }

        manifest = {
            "repo_id": self.REPO_ID,
            "revision": sha,
            "downloaded_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "files": files,
        }

        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return sha

    def batches(self, split: str):
        """Yield Arrow record batches from the selected dataset split."""
        import pyarrow as pa

        if split not in {"train", "test"}:
            raise ValueError("Invalid TACO split")

        shards = sorted((self.raw_dir / split).glob("*.arrow"))

        if not shards:
            raise FileNotFoundError(f"No Arrow shards in {self.raw_dir / split}")

        for shard in shards:
            with pa.memory_map(str(shard), "r") as source:
                yield from pa.ipc.open_stream(source)

    def rows(self, split: str, *, columns: list[str] | None = None, limit: int | None = None) -> Iterator[dict]:
        """Yield dataset records with optional column selection and limits."""
        if limit is not None and (type(limit) is not int or limit < 1):
            raise ValueError("limit must be a positive integer or None")

        count = 0

        for batch in self.batches(split):
            selected = batch.select(columns) if columns else batch
            names = selected.schema.names
            arrays = [selected.column(index) for index in range(len(names))]

            for index in range(selected.num_rows):
                yield {
                    name: column[index].as_py()
                    for name, column in zip(names, arrays)
                }

                count += 1

                if limit is not None and count >= limit:
                    return

    def questions(self, splits: tuple[str, ...] = ("train", "test")) -> Iterator[str]:
        """Yield coding prompts from the selected dataset splits."""
        for split in splits:
            for row in self.rows(split, columns=["question"]):
                yield row["question"]
