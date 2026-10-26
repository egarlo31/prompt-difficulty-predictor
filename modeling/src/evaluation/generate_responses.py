
"""Generate LLM responses and collect experimental statistics."""

import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from inference.ollama_gateway import OllamaGateway
from modeling.src.evaluation.hardware_monitor import HardwareMonitor


@dataclass(frozen=True)
class GenerationConfig:
    """Define reproducible LLM inference settings."""

    model: str = "llama3.1:8b"
    host: str = "http://localhost:11434"
    options: Mapping[str, Any] = field(default_factory=lambda: {
        "temperature": 0.0,
        "seed": 42,
        "num_ctx": 4096,
        "num_predict": 512,
    })
    system: str | None = None
    think: bool | None = False
    keep_alive: str = "10m"
    timeout: int = 300

    def __post_init__(self) -> None:
        if not self.model.strip() or self.timeout <= 0:
            raise ValueError("A model name and positive timeout are required")

        object.__setattr__(self, "options", MappingProxyType(dict(self.options)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize the inference configuration."""
        config = vars(self).copy()
        config["options"] = dict(self.options)
        config["schema_version"] = 1
        return config


class ResponseStatistics:
    """Collect provider timings, token counts, and throughput."""

    DURATION_FIELDS = (
        "total_duration",
        "load_duration",
        "prompt_eval_duration",
        "eval_duration",
    )

    @staticmethod
    def _throughput(tokens: int | None, seconds: float | None) -> float | None:
        """Calculate token throughput when timing data is available."""
        if tokens is None or seconds is None or seconds <= 0:
            return None

        return tokens / seconds

    @classmethod
    def collect(cls, response) -> dict[str, Any]:
        """Preserve Ollama response data and calculate derived metrics."""
        data = response.model_dump(mode="json")

        for name in cls.DURATION_FIELDS:
            value = data.get(name)
            data[f"{name}_seconds"] = value / 1e9 if value is not None else None

        total = data["total_duration_seconds"]
        load = data["load_duration_seconds"]

        data["processing_duration_seconds"] = (
            max(0.0, total - load)
            if total is not None and load is not None else None
        )

        data["prompt_tokens_per_second"] = cls._throughput(
            data.get("prompt_eval_count"),
            data["prompt_eval_duration_seconds"],
        )

        data["output_tokens_per_second"] = cls._throughput(
            data.get("eval_count"),
            data["eval_duration_seconds"],
        )

        return data


class ResponseGenerator:
    """Coordinate LLM inference and experimental statistics."""

    def __init__(self, config: GenerationConfig, *, gateway=None, hardware_monitor: HardwareMonitor | None = None):
        self.config = config
        self.gateway = gateway if gateway is not None else OllamaGateway(config.host, timeout=config.timeout)
        self.hardware_monitor = hardware_monitor
        self.statistics = ResponseStatistics()

    def _generate_response(self, prompt: str):
        """Submit a prompt to the configured LLM."""
        return self.gateway.generate(
            prompt,
            model=self.config.model,
            options=dict(self.config.options),
            keep_alive=self.config.keep_alive,
            system=self.config.system,
            think=self.config.think,
        )

    def _sample(self, samples: list[dict], errors: list[str]) -> bool:
        """Collect one hardware sample and record failures."""
        if self.hardware_monitor is None:
            return False

        try:
            samples.append(self.hardware_monitor.get_hardware_metrics())
            return True
        except Exception as error:
            errors.append(str(error))
            return False

    def _monitor_loop(self, stop_event: threading.Event, samples: list[dict], errors: list[str]) -> None:
        """Periodically collect hardware metrics."""
        monitor = self.hardware_monitor

        if monitor is None:
            return

        while not stop_event.wait(monitor.sample_interval):
            if not self._sample(samples, errors):
                return

    def _start_monitor(self, samples: list[dict], errors: list[str]) -> tuple[threading.Event, threading.Thread | None]:
        """Start hardware monitoring when available."""
        stop_event = threading.Event()
        monitor = self.hardware_monitor

        if monitor is None or monitor.gpu is None or not self._sample(samples, errors):
            return stop_event, None

        thread = threading.Thread(
            target=self._monitor_loop,
            args=(stop_event, samples, errors),
            daemon=True,
        )
        thread.start()

        return stop_event, thread

    def _stop_monitor(self, stop_event: threading.Event, thread: threading.Thread | None, samples: list[dict], errors: list[str]) -> None:
        """Stop monitoring and capture the final sample."""
        stop_event.set()

        if thread is not None:
            thread.join()
            self._sample(samples, errors)

    def generate(self, prompt: str, attempt: int = 1) -> dict[str, Any]:
        """Generate one response and collect experiment metrics."""
        if attempt < 1:
            raise ValueError("attempt must be positive")

        record: dict[str, Any] = {
            "prompt": prompt,
            "attempt": attempt,
            "model": self.config.model,
            "inference_config": dict(self.config.options),
            "generation_config": self.config.to_dict(),
            "prompt_length_chars": len(prompt),
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
        }

        samples: list[dict] = []
        errors: list[str] = []

        stop_event, thread = self._start_monitor(samples, errors)
        start = time.perf_counter()

        try:
            response = self._generate_response(prompt)
            record.update(self.statistics.collect(response))
            record["status"] = "generated"

        except Exception as error:
            record.update(status="generation_error", error=str(error))

        finally:
            record["wall_time_seconds"] = time.perf_counter() - start
            self._stop_monitor(stop_event, thread, samples, errors)

        monitor = self.hardware_monitor
        record["resources"] = monitor.calculate_resource_metrics(samples) if monitor is not None and samples else {}
        record["hardware_samples"] = samples

        if errors:
            record["monitoring_errors"] = errors

        return record