"""Data contracts for an execution worker; no execution implementation here."""
from dataclasses import asdict, dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class SandboxLimits:
    wall_time_seconds: int = 5
    memory_mb: int = 256
    cpu_count: int = 1
    process_count: int = 32
    output_bytes: int = 65536
    network_enabled: bool = False

    def __post_init__(self):
        for key in ("wall_time_seconds", "memory_mb", "cpu_count", "process_count", "output_bytes"):
            if getattr(self, key) <= 0:
                raise ValueError(f"{key} must be positive")
        if self.network_enabled:
            raise ValueError("Network must remain disabled for generated-code tasks")

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class SandboxResult:
    task_id: str
    status: Literal["passed", "wrong_answer", "timeout", "runtime_error", "infrastructure_error"]
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    wall_time_seconds: float | None = None


class SandboxRunner(Protocol):
    def run(self, task: dict) -> SandboxResult:
        """Execute a validated task in an isolated worker, never in the notebook."""
        ...
