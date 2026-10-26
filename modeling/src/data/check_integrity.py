"""Structural integrity audit for TACO (audit checks 3, 6 and 8, plus counts).

Reads the raw Arrow files (never modifies them) and writes:
  - modeling/results/integrity_report.json   (small, can be committed)
  - modeling/data/interim/integrity_flags.csv (per-problem flags, git-ignored)

Usage (from the modeling/ folder):
    python src/data/check_integrity.py
    python src/data/check_integrity.py --limit 500     # quick test
"""

import argparse
import ast
import csv
import json
from collections import Counter
from pathlib import Path

MODELING = Path(__file__).resolve().parents[2]
RAW_DIR = MODELING / "data" / "raw" / "TACO"
REPORT = MODELING / "results" / "integrity_report.json"
FLAGS = MODELING / "data" / "interim" / "integrity_flags.csv"

EXPECTED_ROWS = {"train": 25443, "test": 1000}
LIST_FIELDS = ["raw_tags", "tags", "skill_types"]
PLAIN_FIELDS = ["question", "difficulty", "source", "url", "date"]


from modeling.src.data.taco_dataset import TacoDataset


class TacoIntegrityAuditor:
    def __init__(self, dataset=None, report_path=REPORT, flags_path=FLAGS):
        self.dataset = dataset or TacoDataset(RAW_DIR)
        self.report_path = Path(report_path)
        self.flags_path = Path(flags_path)

    @staticmethod
    def is_empty(value):
        return value is None or (isinstance(value, str) and value.strip() == "")

    @staticmethod
    def parse_json(value):
        return json.loads(value)

    @staticmethod
    def parse_list(value):
        if not isinstance(value, str) or len(value) > 262144:
            raise ValueError("Oversized or non-text list field")
        # literal_eval, never eval(): the data is untrusted text
        return ast.literal_eval(value)

    def audit_rows(self, rows):
        """Audit an iterable of dict-like rows. Returns (stats, flag_rows)."""
        s = Counter()
        sources, difficulty, years = Counter(), Counter(), Counter()
        exec_type = Counter()
        urls = Counter()
        flag_rows = []

        for idx, row in enumerate(rows):
            flags = []
            s["rows"] += 1

            # Plain fields
            for f in PLAIN_FIELDS:
                if self.is_empty(row.get(f)):
                    s[f"empty_{f}"] += 1
                    flags.append(f"empty_{f}")

            # list-like fields stored as strings
            for f in LIST_FIELDS:
                v = row.get(f)
                if self.is_empty(v):
                    s[f"empty_{f}"] += 1
                    continue
                try:
                    self.parse_list(v)
                except (ValueError, TypeError, SyntaxError, AttributeError):
                    s[f"parse_fail_{f}"] += 1
                    flags.append(f"parse_fail_{f}")

            # solutions
            v = row.get("solutions")
            if self.is_empty(v):
                s["no_solutions"] += 1
                flags.append("no_solutions")
            else:
                try:
                    sols = self.parse_json(v)
                    if not sols:
                        s["no_solutions"] += 1
                        flags.append("no_solutions")
                    else:
                        s["total_solutions"] += len(sols)
                except (ValueError, TypeError, SyntaxError, AttributeError):
                    s["parse_fail_solutions"] += 1
                    flags.append("parse_fail_solutions")

            # tests
            v = row.get("input_output")
            if self.is_empty(v):
                s["no_tests"] += 1
                exec_type["no_tests"] += 1
                flags.append("no_tests")
            else:
                try:
                    io = self.parse_json(v)
                    ins, outs = io.get("inputs") or [], io.get("outputs") or []
                    if not ins or not outs:
                        s["no_tests"] += 1
                        exec_type["no_tests"] += 1
                        flags.append("no_tests")
                    else:
                        s["total_tests"] += len(ins)
                        if len(ins) != len(outs):
                            s["tests_length_mismatch"] += 1
                            flags.append("tests_length_mismatch")
                        if len(set(map(str, ins))) < len(ins):
                            s["tests_with_duplicate_inputs"] += 1
                        exec_type["function" if io.get("fn_name") else "stdin"] += 1
                except (ValueError, TypeError, SyntaxError, AttributeError):
                    s["parse_fail_input_output"] += 1
                    exec_type["unparseable"] += 1
                    flags.append("parse_fail_input_output")

            # images
            try:
                if int(row.get("picture_num") or 0) > 0:
                    s["with_images"] += 1
                    flags.append("has_images")
            except (ValueError, TypeError):
                s["parse_fail_picture_num"] += 1
                flags.append("parse_fail_picture_num")

            sources[row.get("source")] += 1
            difficulty[row.get("difficulty")] += 1
            d = row.get("date")
            years[d[:4] if isinstance(d, str) and len(d) >= 4 else "unknown"] += 1
            if not self.is_empty(row.get("url")):
                urls[row["url"]] += 1

            if flags:
                flag_rows.append(
                    {
                        "idx": idx,
                        "source": row.get("source"),
                        "url": row.get("url"),
                        "flags": ";".join(flags),
                    }
                )

        stats = {
            "counts": dict(s),
            "by_source": dict(sources),
            "by_difficulty": dict(difficulty),
            "by_year": dict(sorted(years.items())),
            "execution_type": dict(exec_type),
            "duplicate_urls_within_split": sum(1 for c in urls.values() if c > 1),
        }
        return stats, flag_rows, set(urls)

    def run(self, *, limit=None):
        report, all_flags, url_sets = {}, [], {}
        for split in ["train", "test"]:
            print(f"Auditing {split}...")
            ds = self.dataset.rows(split, limit=limit)
            stats, flag_rows, urls = self.audit_rows(ds)
            n = stats["counts"]["rows"]
            stats["expected_rows"] = EXPECTED_ROWS[split]
            stats["row_count_matches"] = (
                (n == EXPECTED_ROWS[split]) if not limit else None
            )
            report[split] = stats
            url_sets[split] = urls
            all_flags += [{"split": split, **r} for r in flag_rows]

        report["train_test_url_overlap"] = len(url_sets["train"] & url_sets["test"])

        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        self.report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        self.flags_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.flags_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["split", "idx", "source", "url", "flags"])
            w.writeheader()
            w.writerows(all_flags)

        for split in ["train", "test"]:
            print(f"\n== {split} ==")
            for k, v in sorted(report[split]["counts"].items()):
                print(f"  {k}: {v}")
            print("  execution_type:", report[split]["execution_type"])
        print("\ntrain/test url overlap:", report["train_test_url_overlap"])
        print(f"\nReport: {self.report_path}\nFlags:  {self.flags_path}")
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    TacoIntegrityAuditor().run(limit=args.limit)


if __name__ == "__main__":
    main()
