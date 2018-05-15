from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from .enums import MeasureOperator


class MeasureFilterSchema(Schema):
    _measure_name = fields.String(data_key="measureName")
    _value = fields.Decimal(data_key="value")
    _operator = EnumField(MeasureOperator, by_value=True, data_key="membershipType")
    _end_value = fields.Decimal(data_key="endValue")
