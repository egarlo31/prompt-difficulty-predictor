# Prompt ID traceability verification

**Finding: response-to-text traceability works; original dataset-record
traceability is not preserved end to end.** Verified read-only on 2026-10-26.

## Current chain

| Stage | Identifier/data retained | Limitation |
|---|---|---|
| TACO Arrow | Source metadata; a row can be located by revision, split and sorted-shard index. | No native `id`/`question_id` column exists in these shards. |
| `TacoDataset.questions()` | Question text only. | Drops split/index and all metadata. |
| `PromptOperation` JSONL export | `{"prompt": "..."}`. | The deduplication hash is used internally but not written; no dataset key is retained. |
| Main notebook sample | A bounded list of strings. | No provenance object is passed to generation. |
| `BatchGenerator` | SHA-256 `prompt_id`, attempt and `response_id`. | The ID identifies normalized text, not its source row. |
| `ResponseGenerator.generate()` alone | Prompt, response and experiment statistics. | Does not assign `prompt_id`; the batch adds it. |
| Backend/browser prediction | Prompt and target-model string. | No dataset ID is accepted, returned or persisted. |

The batch identifier is exactly:

```python
hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()
```

Leading/trailing whitespace is ignored; interior whitespace and case remain
significant. The same normalized text always receives the same content ID,
regardless of source, split, URL or dataset revision.

The saved response key is:

```text
<run-directory-name>:<prompt_id>:<attempt>
```

The batch also accepts a dictionary containing `prompt` and an optional
`prompt_id`. If supplied, that ID must equal the computed text hash. Passing
an original dataset ID in that field is rejected. Other dataset metadata is
not propagated into the saved record.

## Direct checks on local artifacts

- Read all 10 Arrow shards: 26,443 rows and 25,816 unique normalized text hashes.
- Read all 25,816 rows of `modeling/data/processed/prompts.jsonl`: every record
  has only `prompt`; all match TACO text hashes and none is duplicated there.
- Read the six difficulty exports: every record also contains only `prompt`
  and matches a raw TACO text. Difficulty exports are deduplicated separately.
- Found 546 hashes belonging to multiple raw rows, representing 627 extra
  occurrences. A content-hash join is one-to-many for those prompts.
- Recomputed IDs in all three saved pilot responses: 3/3 `prompt_id` values
  and 3/3 `response_id` values match their formulas.
- None of those response records contains dataset revision, split, row index,
  original question ID, URL or a provenance object.
- Confirmed that an arbitrary original dataset ID is rejected as `prompt_id`.
- No local LiveCodeBench source files exist, so a real `question_id` join
  cannot be tested. Its notebook code exports only `question_content`.

### Pilot source matches

| Saved content ID prefix | Original TACO row matches | ID formulas correct |
|---|---|---|
| `e0e1a40c9f75…` | `train:0`, `train:15817` | Yes |
| `f6e6e2933845…` | `train:1` | Yes |
| `b024a891ac3b…` | `train:2` | Yes |

The first saved prompt occurs at `train:0` with URL
`https://codeforces.com/problemset/problem/1063/C` and at `train:15817` with URL
`https://codeforces.com/problemset/problem/1064/E`. These are different source
records sharing the normalized text. Their tests must not be chosen arbitrarily.
The other two pilot texts each have one match in this local snapshot, but their
source keys are still not saved with the responses.

## Candidate IDs do not close this gap

`CandidateSelector` constructs `(split, idx)` identifiers, but the main notebook
does not consume that candidate table. `DatasetManager` currently validates
uniqueness using only `idx`; that is not a complete TACO key when both splits
are combined. Neither path persists a mapping from those keys to the batch hash.

## Minimum change needed later — not implemented here

Keep the existing content hash for deduplication/resume and store a small
provenance table alongside it:

- `prompt_id`: the existing normalized-text hash.
- Dataset name and pinned revision/version.
- TACO `split` and row `idx`; for LiveCodeBench, its native `question_id` and
  enough source context to identify the original record.

Retain one mapping row per original occurrence when text is duplicated. This
can be a CSV or JSONL file; it does not require a database or new service.
Use that explicit mapping when attaching tests and persist the selected source
key with the eventual evaluation result.

**Until that mapping is implemented, the project can identify the text of each
batch response, but cannot guarantee which original dataset problem/tests it
belongs to.** No source code, notebook, data export or response history was
modified to perform this verification.

## Review scope and checks

The review covered the 12 repository Python source/test files, all three
notebooks, backend schemas/routes, shared Ollama transport and frontend source.
Python and notebook syntax checks passed. All four existing API tests passed;
these test the provisional API contract, not LLM correctness or provenance.
Documentation links and the retained diagram XML parsed successfully.
No new inference or generated-solution execution was performed.

A before/after hash comparison confirmed all 30 tracked non-documentation files
(excluding the explicitly removed `.gitkeep` placeholders) were unchanged.
JavaScript was inspected as source; no browser interaction test was run.
