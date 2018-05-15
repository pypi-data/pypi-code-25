from marshmallow import Schema, fields, post_load


class AttributeSchema(Schema):
    attribute_name = fields.String(load_from="attributeName")
    code = fields.Int(load_from="code")
