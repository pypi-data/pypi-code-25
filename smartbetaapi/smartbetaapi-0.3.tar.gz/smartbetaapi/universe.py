from .apiservice import APIService
import datetime


class Universe:
    def __init__(self, api_service: APIService, entity_ids: []):
        """The Universe class is used to query data from the system.

        The entity_ids property is the list of entities for which
        data will be retrieved. The entity_ids are set at definition of the Universe. If the
        set of entity_ids changes, create a new Universe for the new set.

        get_data() method is used to query the data in the system.

        Args:
            api_service : Reference to the api service.
            entity_ids:  List of entity ids

        """
        self._entity_ids = []
        self._api_service = api_service
        self._entity_ids = entity_ids

    @property
    def entity_ids(self):
        """entity_ids [int]: List of entity Ids that define the Universe.

        """
        return self._entity_ids

    def get_data(self, query_items: [], active_date: datetime = datetime.date(9999,12,31)) -> []:
        """Queries for data in the system

        When specifying QueryItems that have a parent entity context use the following convention: 
        "QueryItemKey?ParentEntityIdentifier"  
        
        e.g. 'Bmk:Measure:weight?MSCI AC' -> gets the bmk wgt in Msci AC World

        Args:
            query_items: The list of query items to retrieve.
                (use APIService.get_all_query_items() to see full list of query items in the system.)
            active_date: The active date for the data. If not specified the latest data available is returned.

        Returns:
            [] of data. Sedol, EntityId and CompanyName are returned by default.

        """
        return self._api_service.get_data_by_query_item(entity_ids=self._entity_ids, query_items=query_items, active_date=active_date)

    def get_data_by_strategy(self, strategy, active_date: datetime = datetime.date(9999,12,31),) -> []:
        """Get data for a pre-defined list of QueryItems in the system.

        Args:
            strategy: The name of the strategy to retrieve
                (use APIService.get_all_strategies() to see full list of strategies in the system.)
            active_date: The active date for the data. If not specified the latest data available is returned.

        Returns:
            [] of data. Sedol, EntityId and CompanyName are returned by default.

        """
        return self._api_service.get_data_by_strategy(self._entity_ids, strategy, active_date)
