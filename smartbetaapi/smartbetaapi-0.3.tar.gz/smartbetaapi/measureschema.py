from marshmallow import Schema, fields


class MeasureSchema(Schema):
    measure_id = fields.String(data_key="measureId")
    measure_name = fields.String(data_key="measureName")