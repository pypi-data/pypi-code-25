from .apiservice import APIService
from .attributefilter import AttributeFilter
from .membershipfilter import MembershipFilter
from .measurefilter import MeasureFilter
from .universecontextmodel import UniverseContextModel
from .enums import JoinType
import datetime


class UniverseContext:
    def __init__(self,
                 api_service: APIService,
                 active_date: datetime = datetime.date(9999,12,31),
                 attribute_filter: AttributeFilter=None,
                 membership_filter: MembershipFilter=None,
                 measure_filter: MeasureFilter=None,
                 attribute_join_type: JoinType = JoinType.AND,
                 membership_join_type: JoinType = JoinType.AND,
                 measure_join_type: JoinType = JoinType.AND,
                 filter_join_type: JoinType = JoinType.AND):
        """The UniverseContext class is used to define a Universe of entities.

        There are three filter types that can be used to define a context:
            MembershipFilter - filters for entities that are members of a parent entity. e.g. entities in MSCI Europe
            AttributeFilter - filters for attributes of an entity. e.g. all entities where GIGS sector is Energy
            ValueFilter - filters for measures of an entity. e.g. Market Cap > 100,000,000

        Multiple filters of each type may be specified. Filters of a given type are joined together by  attribute_join_type,
        measure_join_type or membership_join_type. The different filter types are overall joined together by filter_join_type property.

        Once the filters have been set, get_universe() applies the filters in the system and returns the resultant list of entity ids.

        Args:
            api_service: Reference to the API Service.
            active_date: If not provided, the latest active date is used.
            attribute_filter: An attribute filter to define the universe.
            membership_filter (optional): A membership filter to define the universe.
            measure_filter (optional): A measure filter to define the universe.
            attribute_join_type (optional): Define how attribute filters are joined. Default = JoinType.AND
            membership_join_type (optional): Define how membership filters are joined. Default  = JoinType.AND,
            measure_join_type (optional): Define how measure filters are joined. Default  = JoinType.AND,
            filter_join_type (optional): Define how overall the three filter types are joined. Default  = JoinType.AND
        """
        self._api_service = api_service
        self._model = UniverseContextModel(
            active_date=active_date,
            attribute_filter=attribute_filter,
            membership_filter=membership_filter,
            measure_filter=measure_filter,
            attribute_join_type=attribute_join_type,
            membership_join_type=membership_join_type,
            measure_join_type=measure_join_type,
            filter_join_type=filter_join_type)

    def add_attribute_filter(self, attribute_filter: AttributeFilter, join_type: JoinType = JoinType.AND):
        """Add an attribute filter

        Args:
            attribute_filter: The attribute filter to add.
            join_type (optional): The join type to apply for all attribute filters. Default = JoinType.AND
        """
        self._model.add_attribute_filter(attribute_filter=attribute_filter, join_type=join_type)

    def add_membership_filter(self, membership_filter: MembershipFilter, join_type: JoinType = JoinType.AND):
        """Add a membership filter

        Args:
            membership_filter: The membership filter to add.
            join_type (optional): The join type to apply for all membership filters. Default = JoinType.AND
        """
        self._model.add_membership_filter(membership_filter=membership_filter, join_type=join_type)

    def add_measure_filter(self, measure_filter: MeasureFilter, join_type: JoinType = JoinType.AND):
        """Add a measure filter

        Args:
            measure_filter: The measure filter to add.
            join_type (optional): The join type to apply for all measure filters. Default = JoinType.AND
        """
        self._model.add_measure_filter(measure_filter=measure_filter, join_type=join_type)

    def get_universe(self) -> []:
        """Apply the universe context filters to get a Universe of Entity Ids

        """
        entity_ids = self._api_service.get_universe(model_to_send=self._model)
        return entity_ids
