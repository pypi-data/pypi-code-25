import unittest
from smartbeta_api.enums import AttributeOperator
from smartbeta_api.attributefilter import AttributeFilter


class TestAttributeFilter(unittest.TestCase):

    def test_AttributeFilter(self):
        test_filter = AttributeFilter(query_item_key='FS_C:Attribute:GIGS.Level.2',
                                      values=['Banks', 'Diversified Financials'],
                                      operator=AttributeOperator.IN)
        self.assertEqual(test_filter._values, ['Banks', 'Diversified Financials'])
        self.assertEqual(test_filter._operator, AttributeOperator.IN)
        self.assertEqual(test_filter._query_item_key, 'FS_C:Attribute:GIGS.Level.2')


if __name__ == '__main__':
    unittest.main()
