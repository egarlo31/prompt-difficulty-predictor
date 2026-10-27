# Current scope

## Data preparation

- `TacoDataset` downloads pinned Arrow shards and reads selected columns by split.
- `TacoIntegrityAuditor` checks structural fields, tests, solutions and image flags.
- `CandidateSelector` creates a filtered candidate table after a complete audit.
- `DatasetManager` loads a candidate CSV; its current validation treats `idx`
  alone as unique, although TACO indices are local to a split.
- `PromptOperation` exports only prompt text and deduplicates normalized text.

The main notebook exports all raw TACO questions by default. It does not load or
apply `candidate_ids.csv`, so the prompt-only export is not the filtered candidate set.

## Experimental generation

`ResponseGenerator` owns inference configuration and generation statistics.
`BatchGenerator` owns sequential processing, saved attempts, configuration checks,
file locking and resume. `OllamaGateway` only handles provider communication.

Hardware sampling is optional. The current `HardwareMonitor` uses NVIDIA/NVML;
it is not a general Apple GPU monitor. `BatchGenerator` accepts an optional memory
guard object, but no corresponding guard implementation is present in the source
tree and the notebook does not configure one.

## Application

FastAPI provides `/api/v1/health` and `/api/v1/predict`. The frontend submits the
prompt to the API and falls back to a separate local JavaScript heuristic when
no API response is available. Backend and fallback rules are not identical.
The backend can also serve the frontend as static files.

Neither path evaluates generated code or provides validated difficulty labels.
The application request and response schemas do not contain a dataset prompt ID.

## Not implemented

- A sandbox or test runner for generated solutions.
- A stored join between response prompt hashes and source dataset records/tests.
- Measured pass rates, a labeled training set or a trained predictor.
- Model training, checkpoints, automated deployment or additional provider integrations.

The repository does not need a database or additional services to document the
current work. Pending items should be implemented only when required by the
next experiment.
