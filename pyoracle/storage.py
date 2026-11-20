"""SQLite persistence for reputation and historical feeds."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import PriceFeed


class OracleStorage:
    def __init__(self, db_path: str = "pyoracle.db"):
        self.db_path = db_path
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reputation (
                    source_id TEXT PRIMARY KEY,
                    score REAL NOT NULL,
                    observations INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feeds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    confidence REAL NOT NULL,
                    sources_used INTEGER,
                    sources_total INTEGER,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feeds_symbol ON feeds(symbol)")

    def save_reputation(self, scores: Dict[str, float], observations: Dict[str, int]):
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            for sid, score in scores.items():
                obs = observations.get(sid, 0)
                conn.execute(
                    """INSERT INTO reputation (source_id, score, observations, updated_at)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(source_id) DO UPDATE SET
                           score=excluded.score,
                           observations=excluded.observations,
                           updated_at=excluded.updated_at""",
                    (sid, score, obs, now),
                )

    def load_reputation(self) -> tuple[Dict[str, float], Dict[str, int]]:
        scores, obs = {}, {}
        with self._conn() as conn:
            for sid, score, o in conn.execute("SELECT source_id, score, observations FROM reputation"):
                scores[sid] = score
                obs[sid] = o
        return scores, obs

    def save_feed(self, feed: PriceFeed):
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO feeds (symbol, price, confidence, sources_used, sources_total, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (feed.symbol, feed.price, feed.confidence, feed.sources_used,
                 feed.sources_total, feed.timestamp.isoformat()),
            )

    def get_recent_feeds(self, symbol: str, limit: int = 20) -> List[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT price, confidence, sources_used, sources_total, timestamp
                   FROM feeds WHERE symbol = ? ORDER BY id DESC LIMIT ?""",
                (symbol, limit),
            ).fetchall()
        return [
            {"price": r[0], "confidence": r[1], "sources_used": r[2],
             "sources_total": r[3], "timestamp": r[4]}
            for r in rows
        ]
