# PyOracle

**Pure Python Decentralized Oracle Aggregator**

Multi-source consensus engine with reputation scoring, anomaly detection, SQLite persistence, and real-time price feeds. Zero external dependencies for core logic. Designed for real-world use in DeFi testing, trading bots, portfolio systems, and on-chain data simulation.

## Why PyOracle?

- **Robust consensus**: Median-of-votes aggregation (Pyth-inspired) + optional reputation-weighted median that resists outliers and single-source manipulation.
- **Reputation system**: Sources earn/lose trust based on historical accuracy and confidence calibration. Scores persist across restarts.
- **Anomaly detection**: Statistical outlier rejection and sudden-move guards.
- **Persistence**: SQLite storage for reputation scores and historical feeds — full audit trail.
- **Production-ready patterns**: Clean architecture, comprehensive tests, CLI, zero-dep core.
- **Usable today**: Library + CLI for aggregating any numeric feed (prices, weather, sports odds, etc.).

## Quick Start

```bash
pip install -e .
python -m pyoracle.cli demo
```

```python
from pyoracle import OracleEngine
from pyoracle.sources import SimulatedSource

# With persistence and weighted consensus
engine = OracleEngine(db_path="oracle.db", use_weighted=True)

engine.add_source(SimulatedSource("binance", base=100.0, noise=0.5))
engine.add_source(SimulatedSource("coinbase", base=100.2, noise=0.8))
engine.add_source(SimulatedSource("kraken", base=99.8, noise=1.2))

feed = engine.aggregate("ETH/USD")
print(f"${feed.price:.2f} ±${feed.confidence:.2f} ({feed.sources_used} sources)")
print("Reliable:", feed.is_reliable)
print("Reputation:", engine.get_reputation())
print("History:", engine.recent_history("ETH/USD"))
```

## Architecture

```
Sources → Normalization → Anomaly Filter → Reputation-weighted Consensus → Final Feed + Confidence
         ↘──────────────────────────────────↗
              SQLite (reputation + historical feeds)
```

See `docs/ARCHITECTURE.md` for full design.

## Features

- Median + confidence interval aggregation (Pyth-style three-vote method)
- Reputation-weighted consensus option
- Anomaly filtering (median deviation)
- Persistent source reputation and feed history (SQLite)
- CLI demo with live reputation evolution
- Fully unit-tested core logic
- Extensible `DataSource` interface for real APIs

## Extending with Real Sources

```python
from pyoracle.sources import DataSource
from pyoracle.models import SourceReport
import urllib.request  # or any HTTP client

class CoinGeckoSource(DataSource):
    def fetch(self, symbol):
        # Implement real HTTP call here
        ...
        return SourceReport(self.source_id, symbol, price, confidence)
```

## License

MIT — see LICENSE
