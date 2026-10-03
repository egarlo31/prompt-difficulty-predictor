"""Download the raw TACO files at a pinned revision.

Only the Arrow shards are downloaded. The dataset's own loading script
(TACO.py) is NOT downloaded or executed.

First run: resolves the latest commit and records it in
modeling/results/taco_manifest.json (commit this file).
Later runs: reuse the revision stored in the manifest, so everyone on the
project gets exactly the same data.

Usage (from the modeling/ folder):
    python src/data/download_taco.py
    python src/data/download_taco.py --revision <commit_hash>
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

REPO_ID = "BAAI/TACO"
MODELING = Path(__file__).resolve().parents[2]
RAW_DIR = MODELING / "data" / "raw" / "TACO"
MANIFEST = MODELING / "results" / "taco_manifest.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", default=None, help="commit hash to pin")
    args = parser.parse_args()

    revision = args.revision
    if revision is None and MANIFEST.exists():
        revision = json.loads(MANIFEST.read_text())["revision"]
        print(f"Using pinned revision from manifest: {revision}")

    sha = HfApi().dataset_info(REPO_ID, revision=revision).sha
    print(f"Resolved revision: {sha}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        revision=sha,
        local_dir=RAW_DIR,
        allow_patterns=["train/*.arrow", "test/*.arrow", "README.md"],
    )

    files = {
        str(p.relative_to(RAW_DIR)).replace("\\", "/"): p.stat().st_size
        for p in sorted(RAW_DIR.glob("*/*.arrow"))
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({
        "repo_id": REPO_ID,
        "revision": sha,
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files": files,
    }, indent=2))
    print(f"Done. {len(files)} files, {sum(files.values()) / 1e9:.2f} GB")
    print(f"Manifest written to {MANIFEST}")


if __name__ == "__main__":
    main()
