import unittest
import tempfile
import os
from pyoracle.engine import OracleEngine
from pyoracle.sources import StaticSource
from pyoracle.storage import OracleStorage


class TestStorage(unittest.TestCase):
    def test_persist_and_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "test.db")
            eng = OracleEngine(db_path=db)
            eng.add_source(StaticSource("a", 100.0))
            eng.add_source(StaticSource("b", 100.5))
            eng.aggregate("BTC")

            # Reload
            eng2 = OracleEngine(db_path=db)
            scores = eng2.get_reputation()
            self.assertIn("a", scores)
            history = eng2.recent_history("BTC")
            self.assertEqual(len(history), 1)
            self.assertAlmostEqual(history[0]["price"], 100.25, places=1)


if __name__ == "__main__":
    unittest.main()
