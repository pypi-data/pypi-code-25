import unittest
import datetime
from smartbeta_api.universequeryitemmodel import UniverseQueryItemModel


class TestUniverseQueryItemModel(unittest.TestCase):

    def test_UniverseQueryItemModel(self):
        active_date = datetime.date(9999, 12, 31)
        model = UniverseQueryItemModel(query_items=["1", "2"], entity_ids=[3, 4], active_date=active_date)
        self.assertEqual(model._query_items, ["1", "2"])
        self.assertEqual(model._entity_ids, [3, 4])
        self.assertEqual(model._active_date, active_date)


if __name__ == '__main__':
    unittest.main()
