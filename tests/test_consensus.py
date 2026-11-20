import unittest
from pyoracle.consensus import aggregate_reports
from pyoracle.models import SourceReport
from datetime import datetime


class TestConsensus(unittest.TestCase):
    def test_single_source(self):
        reports = [SourceReport("a", "ETH", 100.0, 1.0)]
        price, conf = aggregate_reports(reports)
        self.assertAlmostEqual(price, 100.0)
        self.assertGreater(conf, 0)

    def test_outlier_resistance(self):
        reports = [
            SourceReport("good1", "ETH", 100.0, 0.5),
            SourceReport("good2", "ETH", 100.2, 0.5),
            SourceReport("good3", "ETH", 99.8, 0.5),
            SourceReport("bad", "ETH", 50.0, 1.0),  # extreme outlier
        ]
        price, conf = aggregate_reports(reports)
        self.assertGreater(price, 90)  # should stay near 100
        self.assertLess(price, 110)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            aggregate_reports([])


if __name__ == "__main__":
    unittest.main()
