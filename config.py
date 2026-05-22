"""
Central configuration dataclass for SlideCommander.

All runtime settings are held in a single Config instance created by main.py
from CLI arguments and passed to every module. No module mutates Config after
startup; it is effectively immutable once constructed.
"""

from __future__ import annotations

from dataclasses import dataclass

_VALID_MODEL_SIZES: frozenset[str] = frozenset({
    "tiny", "tiny.en",
    "base", "base.en",
    "small", "small.en",
    "medium", "medium.en",
    "large-v1", "large-v2", "large-v3",
})


@dataclass
class Config:
    """Runtime configuration for SlideCommander (FR-06, NFR-05)."""

    port: int = 5000
    model_path: str = "tiny"
    no_voice: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.port, int) or isinstance(self.port, bool):
            raise ValueError(
                f"port must be an integer, got {type(self.port).__name__!r}"
            )
        if not (1024 <= self.port <= 65535):
            raise ValueError(
                f"port must be between 1024 and 65535, got {self.port}"
            )
        if self.model_path not in _VALID_MODEL_SIZES:
            raise ValueError(
                f"model_path {self.model_path!r} is not a valid faster-whisper model size. "
                f"Allowed: {', '.join(sorted(_VALID_MODEL_SIZES))}"
            )

    @property
    def server_url(self) -> str:
        """Return the base URL the server will bind to (port only; IP resolved at runtime)."""
        return f"http://0.0.0.0:{self.port}"
