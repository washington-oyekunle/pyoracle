"""Source reputation scoring based on historical accuracy."""

from typing import Dict
import math


class ReputationStore:
    """In-memory reputation tracker with optional persistence hooks."""

    def __init__(self):
        self._scores: Dict[str, float] = {}
        self._observations: Dict[str, int] = {}

    def get(self, source_id: str) -> float:
        return self._scores.get(source_id, 1.0)

    def get_observations(self) -> Dict[str, int]:
        return dict(self._observations)

    def load(self, scores: Dict[str, float], observations: Dict[str, int]):
        self._scores.update(scores)
        self._observations.update(observations)

    def update(self, source_id: str, reported_price: float, consensus_price: float, confidence: float):
        """Update reputation after a consensus round."""
        obs = self._observations.get(source_id, 0) + 1
        self._observations[source_id] = obs

        deviation = abs(reported_price - consensus_price)
        rel = deviation / max(confidence, 0.01)

        if rel <= 1.0:
            delta = 0.08 * (1.0 - rel)
        else:
            delta = -0.12 * min(rel - 1.0, 4.0)

        lr = 1.0 / math.sqrt(obs)
        current = self.get(source_id)
        new_score = max(0.1, min(5.0, current + delta * lr))
        self._scores[source_id] = new_score

    def all_scores(self) -> Dict[str, float]:
        return dict(self._scores)
