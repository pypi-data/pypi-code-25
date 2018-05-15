from .membershipfilter import MembershipFilter
from .measurefilter import MeasureFilter
from .attributefilter import AttributeFilter
from .enums import JoinType
import datetime


class UniverseContextModel:
    def __init__(self,
                 active_date: datetime = datetime.date(9999, 12, 31),
                 attribute_filter: AttributeFilter = None,
                 membership_filter: MembershipFilter = None,
                 measure_filter: MeasureFilter = None,
                 attribute_join_type: JoinType = JoinType.AND,
                 membership_join_type: JoinType = JoinType.AND,
                 measure_join_type: JoinType = JoinType.AND,
                 filter_join_type: JoinType = JoinType.AND):
        self._active_date = active_date
        self._attribute_filters = []
        self._membership_filters = []
        self._measure_filters = []
        self._attribute_join_type = attribute_join_type
        self._membership_join_type = membership_join_type
        self._measure_join_type = measure_join_type
        self._filter_join_type = filter_join_type
        if attribute_filter is not None:
            self._attribute_filters.append(attribute_filter)
        if membership_filter is not None:
            self._membership_filters.append(membership_filter)
        if measure_filter is not None:
                self._measure_filters.append(measure_filter)

    def add_attribute_filter(self, attribute_filter: AttributeFilter, join_type: JoinType = JoinType.AND):
        self._attribute_join_type = join_type
        if attribute_filter is not None:
            self._attribute_filters.append(attribute_filter)

    def add_membership_filter(self, membership_filter: MembershipFilter, join_type: JoinType = JoinType.AND):
        self._membership_join_type = join_type
        if membership_filter is not None:
            self._membership_filters.append(membership_filter)

    def add_measure_filter(self, measure_filter: MeasureFilter, join_type: JoinType = JoinType.AND):
        self._measure_join_type = join_type
        if measure_filter is not None:
            self._measure_filters.append(measure_filter)
