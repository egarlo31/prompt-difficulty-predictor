## LLM Evaluation

The evaluation runner executes a collection of prompts using a
configured LLM and records the inference results and execution
environment.

### Requirements

- Python environment configured
- Ollama running
- Target model installed locally

### Inputs

The runner requires two arguments:

- `--config`: YAML file defining the provider, model and inference parameters.
- `--input`: JSONL file containing the prompts to execute.

### Usage

From the repository root:

```bash
python -m modeling.src.evaluation.run \
  --config modeling/configs/evaluation/llama3_1_8b.yaml \
  --input modeling/data/evaluation/smoke_test.jsonl
```
### Output
Each execution generates an independent run directory:
```text
modeling/experiments/runs/<run_id>/
├── config.yaml
├── environment.json
└── responses.jsonl
```