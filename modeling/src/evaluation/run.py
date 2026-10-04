import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
import platform
import sys

import yaml

from ..llm.ollama_client import OllamaClient

MODELING_ROOT = Path(__file__).resolve().parents[2]


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_prompts(path: str):
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            yield json.loads(line)

def find_model_metadata(
    models: dict,
    model_name: str,
) -> dict | None:
    """Find metadata for the selected Ollama model."""

    for model in models.get("models", []):
        if model.get("name") == model_name:
            return {
                "name": model.get("name"),
                "digest": model.get("digest"),
                "size": model.get("size"),
                "modified_at": model.get("modified_at"),
                "details": model.get("details"),
            }

    return None

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execute reproducible LLM evaluation runs."
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to the evaluation YAML configuration.",
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the JSONL prompt dataset.",
    )

    args = parser.parse_args()

    config = load_config(args.config)

    provider_config = config["provider"]
    model_config = config["model"]
    inference_config = config["inference"]
    generation_config = config["generation"]

    client = OllamaClient(
        base_url=provider_config["base_url"],
        timeout=provider_config["timeout_seconds"],
    )

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_dir = MODELING_ROOT / "experiments" / "runs" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    models = client.list_models()

    model_metadata = find_model_metadata(
        models=models,
        model_name=model_config["name"],
    )

    ollama_version = client.get_version()

    environment = {
        "run_id": run_id,
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "ollama": {
            "base_url": provider_config["base_url"],
            "version": ollama_version.get("version"),
        },
        "model": model_metadata,
    }

    environment_path = output_dir / "environment.json"

    with open(
            environment_path,
            "w",
            encoding="utf-8",
    ) as environment_file:
        json.dump(
            environment,
            environment_file,
            indent=2,
            ensure_ascii=False,
        )

    # Preserve exact configuration used in this run
    shutil.copy(
        args.config,
        output_dir / "config.yaml",
    )

    results_path = output_dir / "responses.jsonl"

    with open(
        results_path,
        "w",
        encoding="utf-8",
    ) as output_file:

        for sample in load_prompts(args.input):

            result = client.generate(
                model=model_config["name"],
                prompt=sample["prompt"],
                options=inference_config,
                stream=generation_config["stream"],
            )

            record = {
                "run_id": run_id,
                "prompt_id": sample["id"],
                "prompt": sample["prompt"],
                "model": model_config["name"],
                "inference_config": inference_config,
                "response": result.get("response"),
                "prompt_tokens": result.get("prompt_eval_count"),
                "output_tokens": result.get("eval_count"),
                "total_duration_ns": result.get("total_duration"),
                "load_duration_ns": result.get("load_duration"),
                "prompt_eval_duration_ns": result.get(
                    "prompt_eval_duration"
                ),
                "eval_duration_ns": result.get("eval_duration"),
            }

            output_file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

            print(f'{sample["id"]} completed')

    print()
    print(f"Run completed: {run_id}")
    print(f"Results: {results_path}")

if __name__ == "__main__":
    main()