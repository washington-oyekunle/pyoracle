# PyOracle Architecture

## Design Goals

1. **Robustness over complexity** — resist single-source manipulation and outliers.
2. **Zero external dependencies** in the core so the library is easy to vendor or embed.
3. **Observable** — every aggregation produces a confidence interval and source breakdown.
4. **Extensible** — new sources are just classes implementing `DataSource.fetch()`.

## Aggregation Algorithm

Inspired by Pyth Network’s price aggregation:

1. Each source submits `(price, confidence)`.
2. Each source contributes **three votes**: `price - conf`, `price`, `price + conf`.
3. Aggregate price = median of all votes.
4. Aggregate confidence = max distance from the median to the 25th / 75th percentile of votes.

This is naturally robust to outliers because a single extreme source only contributes three votes.

## Reputation

After each round:

- Sources whose reported price lies inside their own confidence interval relative to the consensus receive a small positive adjustment.
- Sources that deviate significantly are penalized.
- Learning rate decays with `1/sqrt(observations)` so early noise doesn’t permanently damage a source.

Reputation is currently in-memory; the design allows easy persistence to SQLite.

## Anomaly Layer

Before consensus, a simple median-deviation filter drops reports more than N% away from the median of raw prices. This prevents a coordinated attack of many similar bad sources from dominating if they are still outliers relative to the majority.

## Extension Points

- Implement `DataSource` for real HTTP/WebSocket feeds (CoinGecko, Binance, etc.).
- Add weighted consensus that multiplies vote counts by reputation score.
- Persist reputation and historical feeds to SQLite for audit trails.
- Expose an HTTP/JSON-RPC server for other services to consume feeds.

## Security Considerations

This is a **simulation and aggregation library**, not a production on-chain oracle. For real on-chain use you would still need:

- Economic security (staking / slashing)
- Cryptographic attestation of source data
- Decentralized network of independent operators

PyOracle gives you the mathematical and software foundation to experiment with those designs locally.
