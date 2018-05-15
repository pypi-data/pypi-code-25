import unittest
from smartbeta_api.queryitem import QueryItem
from smartbeta_api.enums import QueryItemType


class TestQueryItem(unittest.TestCase):

    def test_QueryItem(self):
        query = QueryItem(item_type=QueryItemType,
                          query_item_key=1,
                          data_provider_name="DPname",
                          data_feed_name="DFname")
        # Name is not an attribute of QueryItemType

        self.assertEqual(query.item_type, QueryItemType)

        self.assertEqual(query.query_item_key, 1)
        self.assertEqual(query.data_provider_name, "DPname")
        self.assertEqual(query.data_feed_name, "DFname")


if __name__ == '__main__':
    unittest.main()
