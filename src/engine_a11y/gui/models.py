"""Data models for GUI state management."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class BatchItem:
    path: Path
    status: str = "Pending"
    findings_count: int = 0
    critical_count: int = 0
    score: float = 0.0
    remediated_path: Optional[Path] = None
    element_count: int = 0
