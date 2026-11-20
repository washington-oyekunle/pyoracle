"""Anomaly detection helpers."""

from typing import List
from .models import SourceReport


def filter_outliers(reports: List[SourceReport], max_deviation_pct: float = 0.05) -> List[SourceReport]:
    """Drop reports that deviate more than max_deviation_pct from the median price.

    Returns the filtered list (may be empty).
    """
    if len(reports) < 3:
        return reports

    prices = sorted(r.price for r in reports)
    mid = prices[len(prices) // 2]
    if mid == 0:
        return reports

    threshold = abs(mid) * max_deviation_pct
    return [r for r in reports if abs(r.price - mid) <= threshold]


def sudden_move_guard(previous_price: float, new_price: float, max_change_pct: float = 0.10) -> bool:
    """Return True if the move is within acceptable bounds."""
    if previous_price == 0:
        return True
    change = abs(new_price - previous_price) / abs(previous_price)
    return change <= max_change_pct
