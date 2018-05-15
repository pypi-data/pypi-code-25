import unittest
import datetime
from smartbeta_api.universebystrategymodel import UniverseByStrategyModel


class TestUniverseByStrategyModel(unittest.TestCase):
    def test_UniverseByStrategyModel(self):
        uni = UniverseByStrategyModel(strategy="Strategy", entity_ids=[1, 2], active_date=datetime.date(9999, 12, 31))
        self.assertEqual(uni._strategy, "Strategy")
        self.assertEqual(uni._entity_ids, [1, 2])
        self.assertEqual(uni._active_date, datetime.date(9999, 12, 31))


if __name__ == '__main__':
    unittest.main()
