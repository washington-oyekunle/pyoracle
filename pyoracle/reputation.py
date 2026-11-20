"""Source reputation scoring based on historical accuracy."""

from typing import Dict
import math


class ReputationStore:
    """In-memory + optional SQLite-backed reputation tracker.

    Score starts at 1.0 and is adjusted by:
    - Absolute deviation from consensus (penalizes outliers)
    - Confidence calibration (rewards well-calibrated sources)
    """

    def __init__(self):
        self._scores: Dict[str, float] = {}
        self._observations: Dict[str, int] = {}

    def get(self, source_id: str) -> float:
        return self._scores.get(source_id, 1.0)

    def update(self, source_id: str, reported_price: float, consensus_price: float, confidence: float):
        """Update reputation after a consensus round."""
        obs = self._observations.get(source_id, 0) + 1
        self._observations[source_id] = obs

        deviation = abs(reported_price - consensus_price)
        # Normalize deviation relative to confidence (if confidence is tiny, be stricter)
        rel = deviation / max(confidence, 0.01)

        # Penalty grows with relative deviation; reward for being inside confidence
        if rel <= 1.0:
            delta = 0.05 * (1.0 - rel)  # small positive
        else:
            delta = -0.1 * min(rel - 1.0, 5.0)  # capped negative

        # Learning rate decreases with more observations
        lr = 1.0 / math.sqrt(obs)
        current = self.get(source_id)
        new_score = max(0.1, min(5.0, current + delta * lr))
        self._scores[source_id] = new_score

    def all_scores(self) -> Dict[str, float]:
        return dict(self._scores)
