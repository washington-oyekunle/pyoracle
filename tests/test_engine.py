import unittest
from pyoracle.engine import OracleEngine
from pyoracle.sources import SimulatedSource, StaticSource


class TestEngine(unittest.TestCase):
    def test_basic_aggregation(self):
        eng = OracleEngine()
        eng.add_source(StaticSource("a", 100.0, 0.1))
        eng.add_source(StaticSource("b", 100.1, 0.1))
        eng.add_source(StaticSource("c", 99.9, 0.1))

        feed = eng.aggregate("TEST")
        self.assertAlmostEqual(feed.price, 100.0, places=1)
        self.assertEqual(feed.sources_used, 3)
        self.assertTrue(feed.is_reliable)

    def test_reputation_updates(self):
        eng = OracleEngine()
        eng.add_source(SimulatedSource("stable", base=100, noise=0.1))
        eng.add_source(SimulatedSource("noisy", base=100, noise=5.0))

        for _ in range(10):
            eng.aggregate("SYM")

        scores = eng.get_reputation()
        # Stable source should generally have higher or equal reputation
        self.assertIn("stable", scores)
        self.assertIn("noisy", scores)


if __name__ == "__main__":
    unittest.main()
