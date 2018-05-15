from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from .enums import MeasureOperator


class MeasureFilterSchema(Schema):
    _measure_name = fields.String(dump_to="measureName")
    _value = fields.Decimal(dump_to="value")
    _operator = EnumField(MeasureOperator, by_value=True, dump_to="membershipType")
    _end_value = fields.Decimal(dump_to="endValue")
