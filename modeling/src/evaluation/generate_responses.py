"""Evaluate prompts using a shared Ollama adapter and optional resource monitor."""
import threading
import time

from backend.local_llm.ollama_adapter import OllamaAdapter

MODEL = "llama3.1:8b"
OPTIONS = {
    "temperature": 0.0,
    "top_p": 1.0,
    "seed": 42,
    "num_ctx": 4096,
    "num_predict": 512,
}


class EvaluationRunner:
    """Add timing, resource samples and persistence around a shared adapter."""

    def __init__(self, adapter: OllamaAdapter, hardware_monitor=None):
        self.adapter = adapter
        self.hardware_monitor = hardware_monitor

    def evaluate(self, prompt: str) -> dict:
        record = {
            "prompt": prompt,
            "attempt": 1,
            "model": self.adapter.model,
            "inference_config": self.adapter.options.copy(),
        }
        samples = []
        stop_event = threading.Event()
        monitor = None
        if self.hardware_monitor is not None:
            samples.append(self.hardware_monitor.get_hardware_metrics())
            monitor = threading.Thread(
                target=self.hardware_monitor.monitor_resources,
                args=(stop_event, samples), daemon=True,
            )
            monitor.start()

        start = time.perf_counter()
        try:
            response = self.adapter.generate(prompt)
        except Exception as error:
            record.update(status="generation_error", error=str(error))
        else:
            record.update(self._format_response(response), status="generated")
        finally:
            record["wall_time_seconds"] = time.perf_counter() - start
            stop_event.set()
            if monitor is not None:
                monitor.join()
                samples.append(self.hardware_monitor.get_hardware_metrics())

        record["resources"] = (
            self.hardware_monitor.calculate_resource_metrics(samples)
            if self.hardware_monitor is not None else {}
        )
        return record

    @staticmethod
    def _format_response(response) -> dict:
        data = response.model_dump(
            mode="json",
            exclude={"context", "thinking", "logprobs", "image", "completed", "total"},
        )
        for field in ("total_duration", "load_duration", "prompt_eval_duration", "eval_duration"):
            value = data.pop(field, None)
            data[f"{field}_seconds"] = value / 1_000_000_000 if value is not None else None
        total, load = data["total_duration_seconds"], data["load_duration_seconds"]
        data["processing_duration_seconds"] = (
            max(0.0, total - load) if total is not None and load is not None else None
        )
        return data

def main() -> None:
    import argparse
    from pathlib import Path
    from modeling.src.data.prompt_io import load_prompts
    from modeling.src.evaluation.batch import CODING_SYSTEM, generate_batch

    parser = argparse.ArgumentParser(description="Generate responses from prompt JSONL")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--host", default="http://localhost:11434")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    adapter = OllamaAdapter(args.model, host=args.host, options=OPTIONS,
                            system=CODING_SYSTEM, think=False)
    result = generate_batch(load_prompts(args.input, limit=args.limit),
                            EvaluationRunner(adapter), args.run_dir)
    print(result)


if __name__ == "__main__":
    main()
