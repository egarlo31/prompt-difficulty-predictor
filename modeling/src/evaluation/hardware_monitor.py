
"""GPU/RAM sampling and resource summaries for inference evaluation."""

import threading
import time
from itertools import pairwise

import psutil
import pynvml


class HardwareMonitor:
    """Monitor hardware usage during LLM inference."""

    def __init__(self, gpu, sample_interval: float = 0.1):
        if sample_interval <= 0:
            raise ValueError("sample_interval must be positive")

        self.gpu = gpu
        self.sample_interval = sample_interval

    def get_hardware_metrics(self) -> dict:
        """Collect RAM, VRAM, GPU utilization, and power metrics."""
        ram = psutil.virtual_memory()
        vram = pynvml.nvmlDeviceGetMemoryInfo(self.gpu)
        utilization = pynvml.nvmlDeviceGetUtilizationRates(self.gpu)

        try:
            power = pynvml.nvmlDeviceGetPowerUsage(self.gpu) / 1000
        except pynvml.NVMLError:
            power = None

        return {
            "timestamp": time.perf_counter(),
            "ram_gib": ram.used / (1024**3),
            "vram_gib": vram.used / (1024**3),
            "gpu_util_percent": utilization.gpu,
            "gpu_power_w": power,
        }

    def monitor_resources(self, stop_event: threading.Event, samples: list[dict]) -> None:
        """Collect hardware samples until monitoring is stopped."""
        while not stop_event.is_set():
            try:
                samples.append(self.get_hardware_metrics())
            except Exception as error:
                print(f"Monitoring error: {error}")
                return

            stop_event.wait(self.sample_interval)

    @staticmethod
    def _average(samples: list[dict], key: str) -> float | None:
        """Calculate the mean of available metric values."""
        values = [sample[key] for sample in samples if sample[key] is not None]
        return sum(values) / len(values) if values else None

    @staticmethod
    def _estimate_gpu_energy(samples: list[dict]) -> float | None:
        """Estimate GPU energy consumption using trapezoidal integration."""
        if len(samples) < 2 or any(sample["gpu_power_w"] is None for sample in samples):
            return None

        energy = 0.0

        for previous, current in pairwise(samples):
            delta_time = current["timestamp"] - previous["timestamp"]
            average_power = (previous["gpu_power_w"] + current["gpu_power_w"]) / 2
            energy += average_power * delta_time

        return energy

    @staticmethod
    def calculate_resource_metrics(samples: list[dict]) -> dict[str, int | float | None]:
        """Summarize hardware usage and estimated GPU energy."""
        if not samples:
            return {}

        metrics: dict[str, int | float | None] = {"sample_count": len(samples)}

        resources = (
            ("ram", "gib"),
            ("vram", "gib"),
            ("gpu_util", "percent"),
        )

        for name, unit in resources:
            key = f"{name}_{unit}"
            metrics[f"{name}_avg_{unit}"] = HardwareMonitor._average(samples, key)
            metrics[f"{name}_peak_{unit}"] = max(sample[key] for sample in samples)

        metrics["gpu_power_avg_w"] = HardwareMonitor._average(samples, "gpu_power_w")
        metrics["gpu_energy_estimated_j"] = HardwareMonitor._estimate_gpu_energy(samples)

        return metrics
