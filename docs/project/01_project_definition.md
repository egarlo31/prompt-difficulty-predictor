# Project definition

The objective is to estimate the difficulty of coding prompts for a target LLM.
The eventual predictor will require labels derived from actual solution tests.
That predictor and its labeled training dataset are not implemented yet.

## What exists

1. TACO download and read-only Arrow access through `TacoDataset`.
2. Structural auditing and a separate candidate-selection pipeline.
3. Prompt validation, deduplication and JSONL export through `PromptOperation`.
4. Sequential Ollama generation, experiment statistics and resumable response storage.
5. A FastAPI provisional prediction API and an HTML/CSS/JavaScript interface.

The current dataset is TACO. LiveCodeBench has a local-file export notebook,
but its input files are absent in the reviewed checkout. `GenerationConfig`
defaults to `llama3.1:8b`; the construction notebook selects `qwen3:8b` for its
three-prompt pilot. These are configuration choices, not evidence of comparative
model performance.

## Meaning of the outputs

Experimental generation produces response text and execution metadata. It does
not establish whether a solution passes tests.

The application returns Easy, Medium, Hard or Cannot Solve using word counts and
keyword rules. Its confidence and success-rate values are fixed heuristic values,
not probabilities calibrated against real LLM results. The API does not call
Ollama or a trained neural network.

## What remains

Preserve dataset-record provenance, implement isolated solution testing, define
labels from measured results, and then develop and evaluate a predictor.
No architecture or training framework is selected by this document.
