from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from .membershipfilterschema import MembershipFilterSchema
from .measurefilterschema import MeasureFilterSchema
from .attributefilterschema import AttributeFilterSchema
from .enums import JoinType
import datetime

class UniverseContextModelSchema(Schema):
    _active_date = fields.Date(dump_to="activeDate", format="%Y-%m-%d", allow_none=False)
    _membership_filters = fields.Nested(MembershipFilterSchema, many=True, dump_to="membershipFilters")
    _measure_filters = fields.Nested(MeasureFilterSchema, many=True, dump_to="measureFilters")
    _attribute_filters = fields.Nested(AttributeFilterSchema, many=True, dump_to="attributeFilters")
    _attribute_join_type = EnumField(JoinType, by_value=True, dump_to="attributeJoinType")
    _membership_join_type = EnumField(JoinType, by_value=True, dump_to="membershipJoinType")
    _measure_join_type = EnumField(JoinType, by_value=True, dump_to="measureJoinType")
    _filter_join_type = EnumField(JoinType, by_value=True, dump_to="filterJoinType")
