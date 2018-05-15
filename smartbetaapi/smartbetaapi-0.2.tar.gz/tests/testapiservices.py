import unittest
import datetime
from smartbeta_api.apiservice import APIService
from smartbeta_api.universecontextmodel import UniverseContextModel
from smartbeta_api.attributefilter import AttributeFilter
from smartbeta_api.membershipfilter import MembershipFilter


class TestAPIServices(unittest.TestCase):

    def setUp(self):
        self.api_service = APIService('https://smart-beta.intramundi.com/api', 'C:/Users/Mfricaudet/ca-bundle.crt')

    def test_get_universe(self):
        # Create the api service
        self.setUp()

        # Create the model
        active_date = datetime.date(9999, 12, 31)
        attribute_filter = AttributeFilter('FS_C:Attribute:GIGS.Level.2', ['Banks', 'Diversified Financials'])
        membership_filter = MembershipFilter('ATEURC')
        universe_model = UniverseContextModel(active_date=active_date,
                                              attribute_filter=attribute_filter,
                                              membership_filter=membership_filter)

        # Call the tested method
        universe = self.api_service.get_universe(universe_model)

        # Assert the results
        self.assertEquals(universe.entity_ids, ['ids'])  # TODO
        self.assertEquals(universe._api_service, self.api_service)  # TODO

    def test_get_data_by_query_item(self):
        # Create api service
        self.setUp()

        # Create the model
        active_date = datetime.date(9999, 12, 31)
        attribute_filter = AttributeFilter('FS_C:Attribute:GIGS.Level.2', ['Banks', 'Diversified Financials'])
        membership_filter = MembershipFilter('ATEURC')
        universe_model = UniverseContextModel(active_date=active_date,
                                              attribute_filter=attribute_filter,
                                              membership_filter=membership_filter)

        entity_ids = self.api_service.get_universe(universe_model)
        query_items = ["items"]

        # Call the tested method
        data = self.api_service.get_data_by_query_item(entity_ids, query_items, active_date)

        # Assert results
        self.assertEqual(data, "sth")  # TODO

    def test_get_data_by_strategy(self):
        # Create api service
        self.setUp()

        # Create the data
        entity_ids = [1, 2]
        strategy = "Strategy"
        active_date = datetime.date(9999, 12, 31)

        # Call the tested method
        data = self.api_service.get_data_by_strategy(entity_ids, strategy, active_date)

        # Assert results
        self.assertEquals(data, "something")  # TODO

    def test_get_all_(self):
        # Create api service
        self.setUp()

        # Call the methods and assert the results
        self.assertEqual(self.api_service.get_all_parent_entities(), "Parent Entities")  # TODO
        self.assertEqual(self.api_service.get_all_query_items(), "Query items")  # TODO
        self.assertEqual(self.api_service.get_all_strategies(), "Strategies")  # TODO

    def test_get_attribute_query_item_values(self):
        # Create api service
        self.setUp()

        # Call the tested method
        query_item_key = "query item key"
        values = self.api_service.get_attribute_query_item_values(query_item_key)

        # Assert results
        self.assertEqual(values, "values")  # TODO

    def test_get_query_item_keys_for_strategy(self):
        # Create api service
        self.setUp()

        # Call the tested method
        strategy_name = 'FS_C:Attribute:GIGS.Level.1'
        query_item_key = self.api_service.get_query_item_keys_for_strategy(strategy_name)

        #Assert results
        self.assertEqual(query_item_key, "Key")  # TODO

    def test_get_latest_active_date(self):
        # Create api service
        self.setUp()

        # Call tested method and assert results
        self.assert_(self.api_service.get_latest_active_date() == datetime.date(9999, 12, 31))  # TO CHECK

    def test_get_measure_query_item_details(self):
        # Create api service
        self.setUp()

        # Call tested method
        strategy_name = 'FS_C:Measure:FDS.Price'
        details = self.api_service.get_measure_query_item_details(strategy_name)

        # Assert results
        self.assertEqual(details, "Details")  # TODO

    def test_get_attribute_query_item_details(self):
        # Create api service
        self.setUp()

        # Call the tested method
        strategy_name = 'FS_C:Attribute:GIGS.Level.1'
        details = self.api_service.get_attribute_query_item_details(strategy_name)

        # Assert results
        self.assertEqual(details, "Details")  # TODO


if __name__ == '__main__':
    unittest.main()
