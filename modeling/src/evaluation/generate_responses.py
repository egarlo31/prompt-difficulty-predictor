from ollama import Client
from datetime import datetime, timezone
from pathlib import Path

import json
import threading
import time
import psutil
import pynvml

MODEL = "llama3.1:8b"
SAMPLE_INTERVAL = 0.1

OPTIONS = {
    "temperature": 0.0,
    "top_p": 1.0,
    "seed": 42,
    "num_ctx": 4096,
    "num_predict": 512,
}

class HardwareMonitor:

    def __init__(self, gpu, sample_interval: float = 0.1):
        if sample_interval <= 0:
            raise ValueError("sample_interval must be positive")

        self.gpu = gpu
        self.sample_interval = sample_interval

    # ==========================================
    # HARDWARE METRICS
    # ==========================================

    def get_hardware_metrics(self) -> dict:

        ram = psutil.virtual_memory()
        vram = pynvml.nvmlDeviceGetMemoryInfo(self.gpu)
        utilization = pynvml.nvmlDeviceGetUtilizationRates(self.gpu)

        try:
            power = pynvml.nvmlDeviceGetPowerUsage(self.gpu) / 1000
        except pynvml.NVMLError:
            power = None

        return {
            "timestamp": time.perf_counter(),
            "ram_gib": ram.used / (1024 ** 3),
            "vram_gib": vram.used / (1024 ** 3),
            "gpu_util_percent": utilization.gpu,
            "gpu_power_w": power,
        }

    # ==========================================
    # RESOURCE MONITORING
    # ==========================================

    def monitor_resources(
        self,
        stop_event: threading.Event,
        samples: list[dict],
    ) -> None:

        while not stop_event.is_set():

            try:
                samples.append(self.get_hardware_metrics())

            except Exception as error:
                print(f"Monitoring error: {error}")
                return

            stop_event.wait(self.sample_interval)

    # ==========================================
    # RESOURCE ANALYSIS
    # ==========================================

    @staticmethod
    def calculate_resource_metrics(samples: list[dict]) -> dict:

        if not samples:
            return {}

        def average(key):
            values = [
                sample[key]
                for sample in samples
                if sample[key] is not None
            ]
            return sum(values) / len(values) if values else None

        energy_j = None

        if (
            len(samples) >= 2
            and all(sample["gpu_power_w"] is not None for sample in samples)
        ):
            energy_j = 0.0

            for previous, current in zip(samples, samples[1:]):

                delta_time = (
                    current["timestamp"] - previous["timestamp"]
                )

                average_power = (
                    previous["gpu_power_w"] + current["gpu_power_w"]
                ) / 2

                energy_j += average_power * delta_time

        return {
            "sample_count": len(samples),

            "ram_avg_gib": average("ram_gib"),
            "ram_peak_gib": max(
                sample["ram_gib"] for sample in samples
            ),

            "vram_avg_gib": average("vram_gib"),
            "vram_peak_gib": max(
                sample["vram_gib"] for sample in samples
            ),

            "gpu_util_avg_percent": average("gpu_util_percent"),
            "gpu_util_peak_percent": max(
                sample["gpu_util_percent"] for sample in samples
            ),

            "gpu_power_avg_w": average("gpu_power_w"),
            "gpu_energy_estimated_j": energy_j,
        }

class LLMGeneration:

    def __init__(self, client: Client, gpu, model: str, options: dict):
        self.client = client
        self.model = model
        self.options = options.copy()
        self.hardware_monitor = HardwareMonitor(gpu)

    # ==========================================
    # LLM GENERATION
    # ==========================================

    def generate_response(self, prompt: str) -> dict:

        result, elapsed, samples, error = self._run_inference(prompt)

        record = {
            "prompt": prompt,
            "attempt": 1,
            "model": self.model,
            "inference_config": self.options.copy(),
            "wall_time_seconds": elapsed,
            "resources": self.hardware_monitor.calculate_resource_metrics(samples),
        }

        if result is None:
            record["status"] = "generation_error"
            record["error"] = error

        else:
            record.update(self._format_response(result))
            record["status"] = "generated"

        return record

    # ==========================================
    # INFERENCE EXECUTION
    # ==========================================

    def _run_inference(self, prompt: str):

        samples = [self.hardware_monitor.get_hardware_metrics()]
        stop_event = threading.Event()

        monitor = threading.Thread(
            target=self.hardware_monitor.monitor_resources,
            args=(stop_event, samples),
            daemon=True,
        )

        result = None
        error = None

        start_time = time.perf_counter()
        monitor.start()

        try:
            result = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options=self.options,
                keep_alive="10m",
            )

        except Exception as exc:
            error = str(exc)

        finally:
            elapsed = time.perf_counter() - start_time
            stop_event.set()
            monitor.join()

            samples.append(
                self.hardware_monitor.get_hardware_metrics()
            )

        return result, elapsed, samples, error

    # ==========================================
    # RESPONSE FORMATTING
    # ==========================================

    def _format_response(self, response) -> dict:

        data = response.model_dump(
            mode="json",
            exclude={
                "context",
                "thinking",
                "logprobs",
                "image",
                "completed",
                "total",
            },
        )

        data = self.scale_ollama_durations(data)

        total = data.get("total_duration_seconds")
        load = data.get("load_duration_seconds")

        data["processing_duration_seconds"] = (
            max(0.0, total - load)
            if total is not None and load is not None
            else None
        )

        return data

    # ==========================================
    # TIME CONVERSION
    # ==========================================

    @staticmethod
    def scale_ollama_durations(data: dict) -> dict:

        duration_fields = (
            "total_duration",
            "load_duration",
            "prompt_eval_duration",
            "eval_duration",
        )

        for field in duration_fields:
            value = data.pop(field, None)

            data[f"{field}_seconds"] = (
                value / 1_000_000_000
                if value is not None
                else None
            )

        return data

    # ==========================================
    # SAVE RESULTS
    # ==========================================

    def save_results(self, results: list[dict]) -> Path:

        run_id = datetime.now(timezone.utc).strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        modeling_root = Path(__file__).resolve().parents[2]

        output_dir = (
            modeling_root
            / "experiments"
            / "runs"
            / run_id
        )

        output_dir.mkdir(parents=True, exist_ok=False)

        output_path = output_dir / "responses.json"

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                results,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return output_path
    
# ==========================================
# MAIN
# ==========================================

def main() -> None:

    client = Client(
        host="http://localhost:11434",
        timeout=160,
    )

    # Dataset
    prompts = [
        "hello",
        "how are you?",
        "tell me a joke",
    ]

    pynvml.nvmlInit()

    try:
        gpu = pynvml.nvmlDeviceGetHandleByIndex(0)

        # Initialize LLM Generation
        generator = LLMGeneration(
            client=client,
            gpu=gpu,
            model=MODEL,
            options=OPTIONS,
        )

        # ==================================
        # MODEL WARM-UP
        # ==================================

        print("Loading LLM into memory...")

        client.generate(
            model=MODEL,
            prompt="Warm-up.",
            stream=False,
            options={**OPTIONS, "num_predict": 1},
            keep_alive="10m",
        )

        print("Model ready.")

        # ==================================
        # EXPERIMENT EXECUTION
        # ==================================

        print("Starting experiments...")

        results = []

        for prompt in prompts:
            result = generator.generate_response(prompt)
            results.append(result)

            print(f"Prompt: {result['status']}")

        # ==================================
        # SAVE RESULTS
        # ==================================

        output_path = generator.save_results(results)

    finally:
        pynvml.nvmlShutdown()

    print(f"\nProcessed prompts: {len(results)}")
    print(f"Results saved: {output_path}")


if __name__ == "__main__":
    main()