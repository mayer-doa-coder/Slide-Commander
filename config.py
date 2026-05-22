"""
Central configuration dataclass for SlideCommander.

All runtime settings are held in a single Config instance created by main.py
from CLI arguments and passed to every module. No module mutates Config after
startup; it is effectively immutable once constructed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """Runtime configuration for SlideCommander (FR-06, NFR-05)."""

    port: int = 5000
    model_path: str = "vosk-model-en-us-0.22"
    pin: Optional[str] = None
    no_voice: bool = False

    def __post_init__(self) -> None:
        # ── port ──────────────────────────────────────────────────────────
        if not isinstance(self.port, int) or isinstance(self.port, bool):
            raise ValueError(
                f"port must be an integer, got {type(self.port).__name__!r}"
            )
        if not (1024 <= self.port <= 65535):
            raise ValueError(
                f"port must be between 1024 and 65535, got {self.port}"
            )

        # ── pin ───────────────────────────────────────────────────────────
        if self.pin is not None:
            if not isinstance(self.pin, str):
                raise ValueError(
                    f"pin must be a 4-digit string, got {type(self.pin).__name__!r}"
                )
            if not re.fullmatch(r"[0-9]{4}", self.pin):
                raise ValueError(
                    f"pin must be exactly 4 decimal digits (e.g. '1234'), got {self.pin!r}"
                )

    @property
    def server_url(self) -> str:
        """Return the base URL the server will bind to (port only; IP resolved at runtime)."""
        return f"http://0.0.0.0:{self.port}"

    @property
    def pin_enabled(self) -> bool:
        return self.pin is not None
