import unittest
import datetime
from smartbeta_api.universecontext import UniverseContext
from smartbeta_api.apiservice import APIService
from smartbeta_api.attributefilter import AttributeFilter
from smartbeta_api.membershipfilter import MembershipFilter
from smartbeta_api.measurefilter import MeasureFilter
from smartbeta_api.enums import AttributeOperator, MeasureOperator, JoinType
from smartbeta_api.universecontextmodel import UniverseContextModel


class TestUniverseContext(unittest.TestCase):

    def test_UniverseContext(self):
        context = UniverseContext(api_service=APIService,
                                  active_date=datetime.date(9999,12,31),
                                  attribute_filter=AttributeFilter('FS_C:Attribute:GIGS.Level.2', ['Banks', 'Diversified Financials'], AttributeOperator.IN),
                                  membership_filter=MembershipFilter('ATEURC'),
                                  measure_filter=MeasureFilter( "Str", 1.5, MeasureOperator.EQ),
                                  attribute_join_type=JoinType.AND,
                                  membership_join_type=JoinType.OR,
                                  measure_join_type=JoinType.AND,
                                  filter_join_type=JoinType.OR)
        self.assertEqual(context._api_service, APIService)
        self.assertIsNotNone(context._model)


if __name__ == '__main__':
    unittest.main()
