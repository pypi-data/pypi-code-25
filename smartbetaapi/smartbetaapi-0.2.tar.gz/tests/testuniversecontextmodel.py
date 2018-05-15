import unittest
import datetime
from smartbeta_api.universecontextmodel import UniverseContextModel
from smartbeta_api.attributefilter import AttributeFilter
from smartbeta_api.membershipfilter import MembershipFilter
from smartbeta_api.measurefilter import MeasureFilter
from smartbeta_api.enums import JoinType, MeasureOperator


class TestUniverseContextModel(unittest.TestCase):

    def setUp(self):
        self.active_date = datetime.date(9999, 12, 31),
        self.attribute_filter = AttributeFilter('FS_C:Attribute:GIGS.Level.2', ['Banks', 'Diversified Financials'])
        self.membership_filter = MembershipFilter('ATEURC'),
        self.measure_filter = MeasureFilter("Str", 1.5, MeasureOperator.EQ)
        self.model = UniverseContextModel(active_date=self.active_date,
                                          attribute_filter=self.attribute_filter,
                                          membership_filter=self.membership_filter,
                                          measure_filter=self.measure_filter,
                                          attribute_join_type=JoinType.AND,
                                          membership_join_type=JoinType.OR,
                                          measure_join_type=JoinType.AND,
                                          filter_join_type=JoinType.OR)

    def test_UniverseContextModel(self):
        self.setUp()
        self.assertEqual(self.model._active_date, self.active_date)
        self.assertEqual(self.model._attribute_filters[0], self.attribute_filter)
        self.assertEqual(self.model._membership_filters[0], self.membership_filter)
        self.assertEqual(self.model._measure_filters[0], self.measure_filter)
        self.assertEqual(self.model._attribute_join_type, JoinType.AND)
        self.assertEqual(self.model._membership_join_type, JoinType.OR)
        self.assertEqual(self.model._measure_join_type, JoinType.AND)
        self.assertEqual(self.model._filter_join_type, JoinType.OR)

    def test_add_attribute_filter(self):
        self.setUp()
        attribute_filter2 = AttributeFilter("Str2", [2, 3])
        self.model.add_attribute_filter(attribute_filter=attribute_filter2, join_type=JoinType.OR)
        self.assertEqual(self.model._attribute_join_type, JoinType.OR)
        self.assertEqual(self.model._attribute_filters, [self.attribute_filter, attribute_filter2])

    def test_add_membership_filter(self):
        self.setUp()
        membership_filter2 = MembershipFilter(2)
        self.model.add_membership_filter(membership_filter2, join_type=JoinType.AND)
        self.assertEqual(self.model._membership_join_type, JoinType.AND)
        self.assertEqual(self.model._membership_filters, [self.membership_filter, membership_filter2])

    def test_add_measure_filter(self):
        self.setUp()
        measure_filter2 = MeasureFilter("Str2", 2.5, MeasureOperator.EQ)
        self.model.add_measure_filter(measure_filter2, join_type=JoinType.OR)
        self.assertEqual(self.model._measure_join_type, JoinType.OR)
        self.assertEqual(self.model._measure_filters, [self.measure_filter, measure_filter2])


if __name__ == '__main__':
    unittest.main()
