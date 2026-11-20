"""Data source abstractions and implementations."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import random

from .models import SourceReport


class DataSource(ABC):
    """Abstract base for any price/data source."""

    def __init__(self, source_id: str):
        self.source_id = source_id

    @abstractmethod
    def fetch(self, symbol: str) -> Optional[SourceReport]:
        """Return a SourceReport or None if unavailable."""
        ...


class SimulatedSource(DataSource):
    """Deterministic + noisy simulated source for testing and demos."""

    def __init__(self, source_id: str, base: float = 100.0, noise: float = 1.0, bias: float = 0.0):
        super().__init__(source_id)
        self.base = base
        self.noise = noise
        self.bias = bias
        self._rng = random.Random(hash(source_id) % (2**32))

    def fetch(self, symbol: str) -> Optional[SourceReport]:
        # Slight drift + noise so different sources disagree realistically
        price = self.base + self.bias + self._rng.gauss(0, self.noise)
        confidence = abs(self._rng.gauss(self.noise * 0.5, self.noise * 0.2))
        return SourceReport(
            source_id=self.source_id,
            symbol=symbol,
            price=round(price, 6),
            confidence=round(max(confidence, 0.01), 6),
            timestamp=datetime.utcnow(),
        )


class StaticSource(DataSource):
    """Fixed price source (useful for unit tests)."""

    def __init__(self, source_id: str, price: float, confidence: float = 0.1):
        super().__init__(source_id)
        self.price = price
        self.confidence = confidence

    def fetch(self, symbol: str) -> Optional[SourceReport]:
        return SourceReport(
            source_id=self.source_id,
            symbol=symbol,
            price=self.price,
            confidence=self.confidence,
        )
