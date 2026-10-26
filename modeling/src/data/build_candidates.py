"""Build the list of candidate problems for the sandbox / pilot.

Applies the audit decisions to the full TACO dataset:
  - exclude sources: kattis (no reference solutions), hackerrank (unclear license)
  - exclude problems flagged: no_solutions, no_tests, has_images,
    parse_fail_*, empty_question

Needs the output of check_integrity.py (full run, not --limit).

Writes:
  - modeling/data/interim/candidate_ids.csv   (git-ignored)
  - modeling/results/candidate_summary.json   (small, commit it)

Usage (from the modeling/ folder):
    python src/data/build_candidates.py
"""

import json
from pathlib import Path

import pandas as pd

from modeling.src.data.check_integrity import FLAGS, RAW_DIR, REPORT
from modeling.src.data.taco_dataset import TacoDataset

MODELING = Path(__file__).resolve().parents[2]
OUT_IDS = MODELING / "data" / "interim" / "candidate_ids.csv"
OUT_SUMMARY = MODELING / "results" / "candidate_summary.json"

EXCLUDED_SOURCES = {"kattis", "hackerrank"}
EXCLUDED_FLAGS = [
    "no_solutions",
    "no_tests",
    "has_images",
    "parse_fail",
    "empty_question",
    "tests_length_mismatch",
]


class CandidateSelector:
    def __init__(self, dataset=None):
        self.dataset = dataset or TacoDataset(RAW_DIR)

    @staticmethod
    def check_flags_match_report(flags, report):
        """Make sure integrity_flags.csv comes from the same full run as the report."""
        for split in ["train", "test"]:
            if report[split].get("row_count_matches") is not True:
                raise ValueError(
                    "Candidate selection requires a complete integrity audit"
                )
            f = flags.loc[flags["split"] == split, "flags"].fillna("")
            for key in ["no_solutions", "no_tests", "has_images"]:
                n_csv = int(f.str.contains(key).sum())
                n_rep = report[split]["counts"].get(
                    key if key != "has_images" else "with_images", 0
                )
                if n_csv != n_rep:
                    raise SystemExit(
                        f"Mismatch in {split}/{key}: flags CSV has {n_csv}, report has {n_rep}. "
                        "Re-run check_integrity.py (full run, without --limit) and try again."
                    )

    @staticmethod
    def select_candidates(meta, flags):
        """meta: DataFrame [split, idx, source, difficulty, url]; flags: DataFrame [split, idx, flags].

        Returns (candidates, summary_dict)."""
        if (
            meta.duplicated(["split", "idx"]).any()
            or flags.duplicated(["split", "idx"]).any()
        ):
            raise ValueError("Duplicate dataset identifiers")
        flags = flags[["split", "idx", "flags"]].copy()
        flags["flags"] = flags["flags"].fillna("")
        df = meta.merge(flags, on=["split", "idx"], how="left", validate="one_to_one")
        df["flags"] = df["flags"].fillna("")

        reasons = {"excluded_source": df["source"].isin(EXCLUDED_SOURCES)}
        for key in EXCLUDED_FLAGS:
            reasons[key] = df["flags"].str.contains(key)

        excluded = pd.concat(reasons, axis=1).any(axis=1)
        candidates = df.loc[~excluded, ["split", "idx", "source", "difficulty"]].copy()
        candidates["has_url"] = df.loc[~excluded, "url"].notna() & (
            df.loc[~excluded, "url"].astype(str).str.strip() != ""
        )

        summary = {
            "total_problems": len(df),
            "excluded_total": int(excluded.sum()),
            "excluded_by_reason_(overlapping)": {
                k: int(v.sum()) for k, v in reasons.items()
            },
            "candidates_total": len(candidates),
            "candidates_by_split": candidates["split"].value_counts().to_dict(),
            "candidates_by_source": candidates["source"].value_counts().to_dict(),
            "candidates_by_taco_difficulty": candidates["difficulty"]
            .fillna("unknown")
            .value_counts()
            .to_dict(),
            "candidates_without_url": int((~candidates["has_url"]).sum()),
        }
        return candidates, summary

    def load_meta(self):
        frames = []
        for split in ("train", "test"):
            rows = self.dataset.rows(split, columns=["source", "difficulty", "url"])
            frames.append(
                pd.DataFrame(
                    {"split": split, "idx": index, **row}
                    for index, row in enumerate(rows)
                )
            )
        return pd.concat(frames, ignore_index=True)

    def run(self):
        if not FLAGS.exists() or not REPORT.exists():
            raise FileNotFoundError("Run the complete integrity audit first")
        flags = pd.read_csv(FLAGS)
        report = json.loads(REPORT.read_text())
        self.check_flags_match_report(flags, report)
        candidates, summary = self.select_candidates(self.load_meta(), flags)
        OUT_IDS.parent.mkdir(parents=True, exist_ok=True)
        candidates.to_csv(OUT_IDS, index=False)
        OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
        OUT_SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))
        return summary


def main():
    CandidateSelector().run()


if __name__ == "__main__":
    main()
