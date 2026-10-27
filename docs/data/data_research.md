# Dataset sources in the current implementation

This page records which sources the code actually handles. It does not imply
that every previously researched dataset is downloaded or supported.

| Dataset | Implemented use | Local status |
|---|---|---|
| TACO (`BAAI/TACO`) | `TacoDataset` download/Arrow access, audit, candidates and prompt export. | 10 Arrow shards and a pinned revision manifest are present. |
| LiveCodeBench | Notebook reads local `test*.jsonl`, groups `question_content` by difficulty and exports prompts. | No source JSONL files are present; real extraction cannot be verified here. |
| APPS, CodeContests, OpenCodeReasoning, GSM8K | No loader or active workflow in the current code. | Not part of the implemented pipeline. |

## TACO

The local dataset card is `modeling/data/raw/TACO/README.md`. The recorded source
is [BAAI/TACO](https://huggingface.co/datasets/BAAI/TACO); the local manifest
records the revision actually used. The [local audit](01_data_audit.md) documents
counts and structural limitations from the checked-out files.

The candidate selector excludes certain sources based on the earlier audit
policy. The all-prompts exporter does not enforce that policy. A prompt export
must not be assumed to be the approved evaluation subset.

## LiveCodeBench

`modeling/notebooks/data/prompts_livecodebench.ipynb` expects local files under
`modeling/data/raw/livecodebench/` with `question_content` and `difficulty`.
It exports only text, so any native `question_id` is discarded by that workflow.
The absence of input files is reported without downloading data or producing
substitute results.

No current source selection, test validity or legal status should be inferred
from old candidate-size estimates or from the existence of an export notebook.
Dataset selection for correctness evaluation is still pending provenance and
test-runner work.
