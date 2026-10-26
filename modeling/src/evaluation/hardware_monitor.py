"""GPU/RAM sampling and resource summaries for inference evaluation."""
import threading
import time

import psutil
import pynvml


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

