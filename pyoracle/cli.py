"""Command-line interface for PyOracle."""

import argparse
import sys

from .engine import OracleEngine
from .sources import SimulatedSource


def cmd_demo(args):
    engine = OracleEngine(db_path=":memory:", use_weighted=True)
    engine.add_source(SimulatedSource("binance", base=3500.0, noise=1.5))
    engine.add_source(SimulatedSource("coinbase", base=3501.5, noise=2.0))
    engine.add_source(SimulatedSource("kraken", base=3498.0, noise=3.5))
    engine.add_source(SimulatedSource("bybit", base=3502.0, noise=1.2))
    engine.add_source(SimulatedSource("okx", base=3499.0, noise=2.2))
    engine.add_source(SimulatedSource("bad_source", base=3400.0, noise=10.0))  # deliberate outlier

    print("Running 8 aggregation rounds for ETH/USD (reputation-weighted)...\n")
    for i in range(8):
        feed = engine.aggregate("ETH/USD")
        print(f"Round {i+1}: ${feed.price:,.2f}  ±${feed.confidence:.2f}  "
              f"({feed.sources_used}/{feed.sources_total})  reliable={feed.is_reliable}")

    print("\nFinal reputation scores:")
    for sid, score in sorted(engine.get_reputation().items(), key=lambda x: -x[1]):
        print(f"  {sid:12} {score:.3f}")

    print("\nRecent history (last 3):")
    for h in engine.recent_history("ETH/USD", 3):
        print(f"  ${h['price']:,.2f} ±{h['confidence']:.2f} @ {h['timestamp']}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pyoracle", description="PyOracle CLI")
    sub = parser.add_subparsers(dest="command")

    demo = sub.add_parser("demo", help="Run a multi-source simulated aggregation demo")
    demo.set_defaults(func=cmd_demo)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
