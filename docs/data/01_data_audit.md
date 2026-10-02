# Data Audit: TACO

**Question:** can reliable difficulty labels, relative to Llama 3 8B, be derived from this dataset?

Raw data is never modified. Outputs go to `modeling/data/interim/` or `processed/`.

## 1. Dataset

| Item | Value |
|---|---|
| Source | https://huggingface.co/datasets/BAAI/TACO (arXiv 2312.14852) |
| Declared size | 26,443 problems (train 25,443 / test 1,000) |
| Revision hash | _TBD (pin it)_ |
| Download date | _TBD_ |

## 2. Checks

Status: `[ ]` pending · `[x]` done

| # | Check | What to verify | Result / decision |
|---|---|---|---|
| [ ] 1 | License | Terms per `source`; HackerRank is unclear. Do not redistribute data in the public repo. | _TBD_ |
| [ ] 2 | Security | Review the loading script; use `ast.literal_eval` instead of `eval`; run solutions only in a sandbox. | _TBD_ |
| [ ] 3 | Integrity | Row counts, parse failures, nulls, `len(inputs) == len(outputs)`. | _TBD_ |
| [ ] 4 | Test validity | Run reference solutions in the sandbox; keep only problems where at least one passes all tests. | _TBD_ |
| [ ] 5 | Output comparison | Define normalization (whitespace, trailing newlines). | _TBD_ |
| [ ] 6 | Duplicates | By `url` and question similarity; train/test overlap. | _TBD_ |
| [ ] 7 | Contamination | Compare Llama 3 pass rate before vs. after its training cutoff (use `date`). | _TBD_ |
| [ ] 8 | Images | Flag or drop problems with `picture_num > 0`. | _TBD_ |
| [ ] 9 | Distribution | Counts by `source`, `difficulty`, `skill_types`; enough easy/medium problems. | _TBD_ |

## 3. Pilot (go / no-go)

Run a stratified sample (~300 problems, by `source` and `difficulty`) before the full dataset.

| Criterion | Target (initial, adjust later) | Observed |
|---|---|---|
| Reference solutions passing their own tests | > ~70-80% | _TBD_ |
| Problems executable (stdin and function formats) | large majority | _TBD_ |
| Largest class share of Llama 3 results | < ~85-90% | _TBD_ |
| Pass-rate gap before vs. after cutoff | not extreme | _TBD_ |

**Decision:** _TBD (go / adjust / replace dataset)_

## 4. Labeling notes

TACO's `difficulty` is for human solvers, not the project label. Labels (Easy / Medium / Hard / Cannot Solve) come from Llama 3 8B pass rate.

- Definition of "solved" and thresholds: _TBD_
- Splits: by problem, stratified by class and `source`.

## 5. Decision log

| Date | Decision | Reason |
|---|---|---|
| _TBD_ | _TBD_ | _TBD_ |

## 6. Citation

Li et al., "TACO: Topics in Algorithmic COde generation dataset", arXiv:2312.14852, 2023.