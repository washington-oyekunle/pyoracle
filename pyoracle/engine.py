"""Main oracle engine that orchestrates sources, filtering, consensus, and reputation."""

from datetime import datetime
from typing import Dict, List, Optional

from .anomaly import filter_outliers
from .consensus import aggregate_reports
from .models import PriceFeed, SourceReport
from .reputation import ReputationStore
from .sources import DataSource


class OracleEngine:
    def __init__(self, max_deviation_pct: float = 0.05):
        self.sources: Dict[str, DataSource] = {}
        self.reputation = ReputationStore()
        self.max_deviation_pct = max_deviation_pct
        self._last_prices: Dict[str, float] = {}

    def add_source(self, source: DataSource):
        self.sources[source.source_id] = source

    def remove_source(self, source_id: str):
        self.sources.pop(source_id, None)

    def aggregate(self, symbol: str) -> PriceFeed:
        """Fetch from all sources, filter, aggregate, update reputation."""
        raw_reports: List[SourceReport] = []
        for src in self.sources.values():
            try:
                report = src.fetch(symbol)
                if report is not None:
                    raw_reports.append(report)
            except Exception:
                # Individual source failures should not crash the oracle
                continue

        if not raw_reports:
            raise RuntimeError(f"no reports available for {symbol}")

        # Anomaly filter
        filtered = filter_outliers(raw_reports, self.max_deviation_pct)
        if not filtered:
            filtered = raw_reports  # fall back rather than fail completely

        price, confidence = aggregate_reports(filtered)

        # Update reputation for every source that reported
        for r in raw_reports:
            self.reputation.update(r.source_id, r.price, price, r.confidence)

        self._last_prices[symbol] = price

        return PriceFeed(
            symbol=symbol,
            price=price,
            confidence=confidence,
            sources_used=len(filtered),
            sources_total=len(raw_reports),
            timestamp=datetime.utcnow(),
            details={
                "reputation": self.reputation.all_scores(),
                "raw_count": len(raw_reports),
            },
        )

    def get_reputation(self) -> Dict[str, float]:
        return self.reputation.all_scores()
