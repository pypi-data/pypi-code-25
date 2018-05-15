from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from .enums import AttributeOperator


class AttributeFilterSchema(Schema):
    _query_item_key = fields.String(data_key="queryItemKey")
    _values = fields.Dict(data_key="values", )
    _operator = EnumField(AttributeOperator, by_value=True, data_key="operator")
