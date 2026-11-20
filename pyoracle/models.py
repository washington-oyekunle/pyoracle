"""Core data models for PyOracle."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SourceReport:
    source_id: str
    symbol: str
    price: float
    confidence: float  # absolute confidence interval (e.g. 0.5 means ±0.5)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.confidence < 0:
            raise ValueError("confidence must be non-negative")


@dataclass
class PriceFeed:
    symbol: str
    price: float
    confidence: float
    sources_used: int
    sources_total: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: dict = field(default_factory=dict)

    @property
    def is_reliable(self) -> bool:
        """Simple reliability heuristic."""
        return self.sources_used >= 3 and self.confidence < self.price * 0.05
