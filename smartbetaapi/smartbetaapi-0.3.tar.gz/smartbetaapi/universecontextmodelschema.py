from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from .membershipfilterschema import MembershipFilterSchema
from .measurefilterschema import MeasureFilterSchema
from .attributefilterschema import AttributeFilterSchema
from .enums import JoinType
import datetime

class UniverseContextModelSchema(Schema):
    _active_date = fields.Date(data_key="activeDate", format="%Y-%m-%d", allow_none=False)
    _membership_filters = fields.Nested(MembershipFilterSchema, many=True, data_key="membershipFilters")
    _measure_filters = fields.Nested(MeasureFilterSchema, many=True, data_key="measureFilters")
    _attribute_filters = fields.Nested(AttributeFilterSchema, many=True, data_key="attributeFilters")
    _attribute_join_type = EnumField(JoinType, by_value=True, data_key="attributeJoinType")
    _membership_join_type = EnumField(JoinType, by_value=True, data_key="membershipJoinType")
    _measure_join_type = EnumField(JoinType, by_value=True, data_key="measureJoinType")
    _filter_join_type = EnumField(JoinType, by_value=True, data_key="filterJoinType")
