from marshmallow import Schema, fields


class MeasureSchema(Schema):
    measure_id = fields.String(load_from="measureId")
    measure_name = fields.String(load_from="measureName")