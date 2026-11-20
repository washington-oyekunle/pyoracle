"""Consensus aggregation algorithms.

Implements a robust median-of-votes approach inspired by Pyth Network:
each source contributes votes at price-confidence, price, and price+confidence.
The aggregate price is the median of all votes; confidence is derived from IQR.
"""

from statistics import median
from typing import List, Tuple

from .models import SourceReport


def aggregate_reports(reports: List[SourceReport]) -> Tuple[float, float]:
    """Return (price, confidence) from a list of reports.

    Raises ValueError if fewer than 1 report.
    """
    if not reports:
        raise ValueError("at least one report required")

    votes: List[float] = []
    for r in reports:
        # Three votes per source: low, mid, high
        votes.append(r.price - r.confidence)
        votes.append(r.price)
        votes.append(r.price + r.confidence)

    votes.sort()
    price = median(votes)

    # Confidence = larger of the distances to 25th/75th percentile of votes
    n = len(votes)
    p25 = votes[n // 4]
    p75 = votes[(3 * n) // 4]
    confidence = max(abs(price - p25), abs(p75 - price))

    return float(price), float(confidence)


def weighted_median(values: List[Tuple[float, float]]) -> float:
    """Weighted median. values = [(value, weight), ...]"""
    if not values:
        raise ValueError("empty")
    sorted_vals = sorted(values, key=lambda x: x[0])
    total = sum(w for _, w in sorted_vals)
    if total <= 0:
        return median([v for v, _ in sorted_vals])
    cumulative = 0.0
    for v, w in sorted_vals:
        cumulative += w
        if cumulative >= total / 2:
            return v
    return sorted_vals[-1][0]
