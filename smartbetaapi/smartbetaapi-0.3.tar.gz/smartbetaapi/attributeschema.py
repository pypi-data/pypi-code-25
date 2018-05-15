from marshmallow import Schema, fields, post_load


class AttributeSchema(Schema):
    attribute_name = fields.String(data_key="attributeName")
    code = fields.Int(data_key="code")
