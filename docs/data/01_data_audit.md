# Data Audit: TACO

**Question:** can reliable difficulty labels, relative to Llama 3 8B, be derived from this dataset?

**Short answer so far:** yes, with limits. After filtering, 18,575 candidate problems remain (17,690 train + 885 test), pending sandbox validation. Contamination cannot be measured with TACO's own dates.

Raw data is never modified. Outputs go to `modeling/data/interim/` or `processed/`.

## 1. Dataset

| Item | Value |
|---|---|
| Source | https://huggingface.co/datasets/BAAI/TACO (arXiv 2312.14852) |
| Declared size | 26,443 problems (train 25,443 / test 1,000) |
| Revision hash | `d593ed0a2becbbc952230bb89be09189bf1056dc` |
| Download date | 2026-10-02 |
| Downloaded | 9 train shards + 1 test shard (Arrow), 4.74 GB. The dataset loading script (`TACO.py`) was not downloaded or executed. |
| Scripts | `modeling/src/data/download_taco.py`, `check_integrity.py` |
| Reports | `modeling/results/integrity_report.json`, `taco_manifest.json` |

## 2. Checks

Status: `[ ]` pending · `[~]` partial · `[x]` done

| # | Check | Result | Decision |
|---|---|---|---|
| [x] 1 | License | Authors' part is Apache 2.0; the data also includes MIT / CC BY 4.0 material. The dataset card states the legal status of HackerRank data is unknown. Terms of the other original platforms were not individually verified. | Exclude HackerRank (810 problems, ~3%). Do not redistribute the data; the repo only holds download scripts and the pinned revision. |
| [x] 2 | Security | Only Arrow files are read. Parsing uses `json.loads` and `ast.literal_eval` (no `eval`). | Run reference solutions only in a sandbox (check 4). |
| [x] 3 | Integrity | Row counts match the declared ones (25,443 / 1,000). `inputs` and `outputs` have equal length in all problems. Total solutions: ~1.54M (declared 1.55M). Parse failures are minimal: 1 `input_output` (train), 10 `solutions` (test). | Review flagged rows in `interim/integrity_flags.csv`; drop unparseable ones. |
| [ ] 4 | Test validity | Not run yet. | Run reference solutions in the sandbox; keep problems where at least one passes all tests. |
| [ ] 5 | Output comparison | Not defined yet. Known case: some expected outputs have extra leading/trailing newlines. | Define normalization before running tests. |
| [~] 6 | Duplicates | Train/test URL overlap: 0, but only for rows that have a URL. 5,224 train problems have no URL (all of Aizu and HackerEarth, 683 of 1,440 AtCoder). | Compare question text for sources without URL. |
| [~] 7 | Contamination | `date` is empty in 75.5% of train (19,222) and 33% of test (332). Only Codeforces and CodeChef have dates. Dates stop in 2023 (143 train, 9 test), so almost nothing is clearly after Llama 3's cutoff (March 2023 per Meta; verify before citing). | Cannot be measured with TACO's dates. Document as a limitation; use LiveCodeBench as external validation; compare pass rates across sources. Do not use "date missing" as a feature. |
| [x] 8 | Images | 630 train and 68 test problems depend on images (`picture_num > 0`). | Exclude. |
| [x] 9 | Distribution | See section 3. | See section 3. |

## 3. Distribution and candidates

Exclusions found in train, by source:

| Source | Problems | No solutions | No tests | Images |
|---|---|---|---|---|
| codeforces | 8,193 | 2,338 | 13 | 231 |
| codechef | 3,352 | 388 | 0 | 91 |
| geeksforgeeks | 2,680 | 0 | 10 | 145 |
| codewars | 2,460 | 0 | 349 | 0 |
| aizu | 2,151 | 736 | 0 | 0 |
| atcoder | 1,440 | 117 | 0 | 0 |
| hackerearth | 2,390 | 1,112 | 174 | 0 |
| leetcode | 777 | 23 | 195 | 0 |
| kattis | 1,236 | 1,235 | 0 | 0 |
| hackerrank | 764 | 1 | 0 | 163 |

Candidates after applying the decisions in section 4 (train and test merged; see `results/candidate_summary.json`):

| Source | Candidates |
|---|---|
| codeforces | 6,161 |
| codechef | 3,125 |
| geeksforgeeks | 2,527 |
| codewars | 2,165 |
| aizu | 1,415 |
| atcoder | 1,323 |
| hackerearth | 1,277 |
| leetcode | 582 |
| **Total** | **18,575** (train 17,690 / test 885) |

Excluded: 7,868 of 26,443 (30%). Reasons overlap: excluded sources 2,046 (Kattis + HackerRank), no solutions 5,950, no tests 741, images 698, parse failures 11.

These are candidates, not validated problems: solutions and tests still have to be checked in the sandbox (check 4).

Other findings:
- Execution format (train): 21,809 stdin, 2,892 function-call, 741 without tests, 1 unparseable. Two harnesses are needed; stdin covers 86%.
- The original test split has only 5 sources (Codeforces and CodeChef are 85%). It does not represent the train distribution.
- 2019 has a spike in dated problems (2,838 train, 262 test). It may be a default value; do not trust it as a real date without checking.
- Many test problems have repeated inputs (925 of 1,000). Deduplicate inputs before execution to save time.
- TACO difficulty among candidates: EASY 7,814, UNKNOWN 3,266, MEDIUM 2,404, MEDIUM_HARD 2,348, HARD 1,763, VERY_HARD 980. It reflects human difficulty; use it only as an auxiliary feature or baseline.
- 3,221 candidates have no URL (Aizu, HackerEarth, part of AtCoder), so duplicates must be checked by question text.

## 4. Decisions so far

1. Exclude: Kattis, HackerRank, and problems without tests, without solutions, or with images.
2. Merge train and test, then build our own split, stratified by source and class (the original test split is not representative).
3. Contamination: documented as a limitation; LiveCodeBench as external validation set.
4. Duplicates: compare question text for sources without URL.
5. Labels: TACO's `difficulty` is for human solvers. Project labels (Easy / Medium / Hard / Cannot Solve) come from Llama 3 8B pass rate. Thresholds are chosen from the observed distribution.

## 5. Pilot (go / no-go)

Run a stratified sample (~300 problems, by `source` and `difficulty`) before the full dataset.

| Criterion | Target (initial, adjust later) | Observed |
|---|---|---|
| Reference solutions passing their own tests | > ~70-80% | _TBD_ |
| Problems executable (stdin and function formats) | large majority | _TBD_ |
| Largest class share of Llama 3 results | < ~85-90% | _TBD_ |
| Pass-rate differences between sources of similar difficulty | no extreme gaps | _TBD_ |

**Decision:** _TBD (go / adjust / replace dataset)_

## 6. Next steps

1. Done: `interim/candidate_ids.csv` generated (18,575 candidates).
2. Build the sandbox and run check 4 and the pilot.
3. Define the output comparison policy (check 5).

## 7. Citation

Li et al., "TACO: Topics in Algorithmic COde generation dataset", arXiv:2312.14852, 2023.