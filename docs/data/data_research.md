# Dataset Research: Reasoning Datasets (T-01)

**Scope:** coding prompts only (as defined in the architecture document).

**Goal:** list candidate datasets to train and evaluate the Prompt Difficulty Predictor, and compare them on what the project needs.

**What the project needs from a dataset**
1. Coding problems with enough volume to train a neural classifier.
2. A way to check automatically whether the target LLM (Llama 3 8B) solved a problem (tests).
3. A spread of difficulty, so that the four classes (Easy / Medium / Hard / Cannot Solve) are all populated.
4. A license that allows our use, and low overlap with data the target LLM may have memorized.

The difficulty label comes from the target LLM's results, not from the dataset's own difficulty field.

"Verified" means the figure was checked against a source during this research. Figures marked **No** come from prior knowledge and must be checked in T-02 before they are final.

## 1. Candidates

| Dataset | Size | Own difficulty field | License | Verified |
|---|---|---|---|---|
| TACO (BAAI) | 26,443 problems (25,443 train / 1,000 test) | Yes (EASY to VERY_HARD) | Mixed: Apache 2.0 for the authors' part, other licenses inside, unclear for HackerRank | Yes (audited, see `01_data_audit.md`) |
| LiveCodeBench | 400 to 880 problems depending on release (v1 to v5); later releases exist | Yes | Listed only as "cc" on the dataset card, to clarify | Partly (releases and sources yes; latest release and exact license not checked) |
| APPS | about 10,000 problems | Yes (introductory / interview / competition) | MIT (from memory) | **No** |
| CodeContests (DeepMind) | about 13,000 training problems | Partial | CC BY 4.0 (from memory) | **No** |
| OpenCodeReasoning(-2) (NVIDIA) | Large | Yes | CC BY 4.0 | Yes (license and sources) |

All five provide problems from competitive programming; tests and reference solutions are available in TACO, LiveCodeBench, APPS and CodeContests.

## 2. Notes per candidate

**TACO.** Largest and most varied. Already audited: about 18.5k usable candidates after filtering. Weaknesses: no dates for 75% of train (contamination cannot be measured with `date`), mixed licenses, two execution formats (stdin and function call).

**LiveCodeBench.** Small, but every problem has a release date, which is exactly what TACO lacks. Problems come from LeetCode, AtCoder and Codeforces. Best option to measure contamination and as an external validation set. Check the latest release and the license wording.

**APPS and CodeContests.** TACO already includes material from both, so they add little as independent sources. They are mainly useful to detect duplicates.

**OpenCodeReasoning.** Built on top of TACO, APPS, CodeContests and open-r1/codeforces. Not an independent source; it only confirms how much these datasets overlap.

## 3. Preliminary reading (not a final decision, that is T-03)

- **TACO** as the main dataset: only candidate with enough volume and difficulty spread.
- **LiveCodeBench** as external validation and contamination check.
- **APPS, CodeContests, OpenCodeReasoning** only for duplicate detection.
- Overlap between code datasets is high. Any combination needs a duplicate check.

## 4. To verify before closing T-02

- Exact license text for LiveCodeBench, APPS and CodeContests, and the terms of the original platforms behind TACO.
- Latest LiveCodeBench release and its current availability.
- Sizes of APPS and CodeContests.
- Llama 3 8B training cutoff, to compare with problem dates.