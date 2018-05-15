from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from .enums import AttributeOperator


class AttributeFilterSchema(Schema):
    _query_item_key = fields.String(dump_to="queryItemKey")
    _values = fields.Dict(dump_to="values", )
    _operator = EnumField(AttributeOperator, by_value=True, dump_to="operator")
