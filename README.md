# PyOracle

**Pure Python Decentralized Oracle Aggregator**

Multi-source consensus engine with reputation scoring, anomaly detection, and real-time price feeds. Zero external dependencies for core logic. Designed for real-world use in DeFi testing, trading bots, portfolio systems, and on-chain data simulation.

## Why PyOracle?

- **Robust consensus**: Median-of-votes aggregation (Pyth-inspired) that resists outliers and single-source manipulation.
- **Reputation system**: Sources earn/lose trust based on historical accuracy and confidence calibration.
- **Anomaly detection**: Statistical outlier rejection and sudden-move guards.
- **Production-ready patterns**: SQLite persistence, clean architecture, comprehensive tests, CLI.
- **Zero-dependency core**: Only Python stdlib. Optional HTTP sources can be plugged in later.
- **Usable today**: Library + CLI for aggregating any numeric feed (prices, weather, sports odds, etc.).

## Quick Start

```bash
pip install -e .
# or just run the examples
python -m pyoracle.cli demo
```

```python
from pyoracle import OracleEngine
from pyoracle.sources import SimulatedSource

engine = OracleEngine()
engine.add_source(SimulatedSource("binance", base=100.0, noise=0.5))
engine.add_source(SimulatedSource("coinbase", base=100.2, noise=0.8))
engine.add_source(SimulatedSource("kraken", base=99.8, noise=1.2))

feed = engine.aggregate("ETH/USD")
print(feed.price, feed.confidence, feed.sources_used)
```

## Architecture

```
Sources → Normalization → Anomaly Filter → Reputation-weighted Consensus → Final Feed + Confidence
         ↘──────────────────────────────────↗
              Historical Accuracy Store (SQLite)
```

See `docs/ARCHITECTURE.md` for full design.

## Features

- Median + confidence interval aggregation
- Reputation scoring (Brier-like + deviation penalties)
- Configurable anomaly thresholds
- Persistent source reputation across restarts
- CLI for live aggregation and inspection
- Fully tested core logic

## License

MIT
