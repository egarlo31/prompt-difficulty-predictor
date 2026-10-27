# Local TACO data audit

Reviewed on 2026-10-26 against local Arrow shards and stored repository reports.
No dataset was downloaded again, no report was regenerated and no solution was run.

## Input snapshot

| Item | Local evidence |
|---|---|
| Dataset | `BAAI/TACO` |
| Revision | `d593ed0a2becbbc952230bb89be09189bf1056dc` |
| Manifest download timestamp | `2026-10-26T08:03:33+00:00` |
| Shards | 9 train and 1 test Arrow file |
| Stored byte total | 4,735,508,104 bytes |
| Rows checked directly | 25,443 train and 1,000 test |
| Native `id` or `question_id` column | Neither is present in these Arrow schemas |

`TacoDataset.download()` downloads Arrow shards and the dataset card; it does
not download or execute the dataset loading script. Stable TACO row keys need
the pinned revision, split and index in sorted-shard order.

## Structural audit and candidates

`TacoIntegrityAuditor` reads `question`, metadata, serialized tests/solutions and
image indicators. It writes `modeling/results/integrity_report.json` and
`modeling/data/interim/integrity_flags.csv`. Its `--limit` option is a partial
structural check, not a complete candidate audit.

The stored report records 5,950 train rows without solutions, 741 without tests,
630 train and 68 test rows with images, one malformed train `input_output`, and
ten malformed test `solutions`. It reports no train/test URL overlap.
These are stored report findings, not new test-execution results.

`CandidateSelector` excludes Kattis/HackerRank and configured structural flags,
including missing tests/solutions, images, parse errors and test-length mismatch.
The stored summary contains 18,575 candidates (17,690 train, 885 test), excluding
7,868 original rows. These candidates have not been validated by running their
reference solutions.

A CSV with those 18,575 rows is present at
`modeling/results/candidate_ids.csv`. The selector and `DatasetManager` use
`modeling/data/interim/candidate_ids.csv` instead; that expected file is absent
in this checkout. The files and paths are not interchangeable automatically.

## Actual prompt export

The main notebook calls `TacoDataset.questions()` over train and test, then
`PromptOperation.export_prompts()`. It does not apply candidate filters.

Direct verification found 25,816 distinct normalized prompt texts in all 26,443
raw rows. The export contains all 25,816 texts, removing 627 repeated occurrences.
No exported text was missing from the raw TACO snapshot. Each exported record
contains only `prompt`; source keys, tests and metadata are not exported.

There are 546 text hashes with more than one original TACO row. Matching by
text alone therefore does not uniquely identify every source problem. Direct
text-hash comparison found no train/test text overlap in this pinned snapshot.

## Limits

- Structural validity does not establish that tests or solutions are correct.
- TACO difficulty describes the source problem, not measured target-LLM success.
- The prompt-only export can contain interactive, image-dependent or otherwise
  unsuitable problems because candidate filtering is not applied.
- Missing dates/URLs limit source-based analysis; no training-contamination
  conclusion is established by this review.
- No sandbox or correctness-labeling pipeline exists yet.

See [the verified prompt-ID findings](02_prompt_traceability.md) before joining
responses to dataset tests.
