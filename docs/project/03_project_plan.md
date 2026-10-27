# Practical project plan

## Current usable workflow

1. Use `TacoDataset` and `PromptOperation` through
   `modeling/notebooks/01_dataset_construction.ipynb`.
2. Reuse the exported `prompts.jsonl` or explicitly rebuild it.
3. Load a bounded sample and select the model/options.
4. Enable `RUN_OLLAMA` only when response generation is intended.
5. Inspect `config.json` and `responses.jsonl` in the selected run directory.

`RUN_OLLAMA` is False by default. Existing runs can only be resumed when the
serialized configuration matches. Older runs may not contain configuration
fields added by the current implementation, such as `timeout`; use a new run ID
when configurations differ.

The two data notebooks export TACO and local LiveCodeBench prompts by difficulty.
A successful notebook run with missing LiveCodeBench files does not validate an
actual LiveCodeBench extraction.

## Immediate next steps

1. **Close the provenance gap.** Preserve each content hash together with its
   dataset revision and source record key. Retain all origins for duplicate text.
2. **Select the evaluation inputs explicitly.** Decide whether to use the existing
   audited candidates instead of all exported questions. Do not equate these sets.
3. **Implement isolated code evaluation.** Recover the correct tests through that
   provenance and distinguish stdin, function-call and interactive problems.
4. **Measure before labeling.** Only tested solutions can contribute to pass rates
   and difficulty labels. Technical generation failures need separate treatment.
5. **Train after labels exist.** Start with a small baseline before choosing a
   neural architecture or a deployment design.

These are pending steps, not features provided by the current code. This
update did not implement any of them or execute generated solutions.
