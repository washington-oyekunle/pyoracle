"""Main oracle engine that orchestrates sources, filtering, consensus, and reputation."""

from datetime import datetime
from typing import Dict, List, Optional

from .anomaly import filter_outliers
from .consensus import aggregate_reports, weighted_median
from .models import PriceFeed, SourceReport
from .reputation import ReputationStore
from .sources import DataSource
from .storage import OracleStorage


class OracleEngine:
    def __init__(self, max_deviation_pct: float = 0.05, db_path: Optional[str] = None, use_weighted: bool = True):
        self.sources: Dict[str, DataSource] = {}
        self.reputation = ReputationStore()
        self.max_deviation_pct = max_deviation_pct
        self.use_weighted = use_weighted
        self.storage = OracleStorage(db_path) if db_path else None
        if self.storage:
            scores, obs = self.storage.load_reputation()
            self.reputation.load(scores, obs)

    def add_source(self, source: DataSource):
        self.sources[source.source_id] = source

    def remove_source(self, source_id: str):
        self.sources.pop(source_id, None)

    def _weighted_aggregate(self, reports: List[SourceReport]) -> tuple[float, float]:
        """Reputation-weighted version of the three-vote median."""
        weighted_votes = []
        for r in reports:
            weight = self.reputation.get(r.source_id)
            # Each of the three votes gets the same weight
            for offset in (-r.confidence, 0.0, r.confidence):
                weighted_votes.append((r.price + offset, weight))
        price = weighted_median(weighted_votes)
        # Confidence still from unweighted IQR for stability
        _, conf = aggregate_reports(reports)
        return price, conf

    def aggregate(self, symbol: str, persist: bool = True) -> PriceFeed:
        raw_reports: List[SourceReport] = []
        for src in self.sources.values():
            try:
                report = src.fetch(symbol)
                if report is not None:
                    raw_reports.append(report)
            except Exception:
                continue

        if not raw_reports:
            raise RuntimeError(f"no reports available for {symbol}")

        filtered = filter_outliers(raw_reports, self.max_deviation_pct)
        if not filtered:
            filtered = raw_reports

        if self.use_weighted and len(filtered) >= 2:
            price, confidence = self._weighted_aggregate(filtered)
        else:
            price, confidence = aggregate_reports(filtered)

        for r in raw_reports:
            self.reputation.update(r.source_id, r.price, price, r.confidence)

        feed = PriceFeed(
            symbol=symbol,
            price=price,
            confidence=confidence,
            sources_used=len(filtered),
            sources_total=len(raw_reports),
            timestamp=datetime.utcnow(),
            details={
                "reputation": self.reputation.all_scores(),
                "raw_count": len(raw_reports),
                "weighted": self.use_weighted,
            },
        )

        if persist and self.storage:
            self.storage.save_feed(feed)
            self.storage.save_reputation(
                self.reputation.all_scores(),
                self.reputation.get_observations(),
            )

        return feed

    def get_reputation(self) -> Dict[str, float]:
        return self.reputation.all_scores()

    def recent_history(self, symbol: str, limit: int = 10):
        if not self.storage:
            return []
        return self.storage.get_recent_feeds(symbol, limit)
