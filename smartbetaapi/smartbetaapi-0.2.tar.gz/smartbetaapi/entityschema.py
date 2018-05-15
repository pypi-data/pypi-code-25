from marshmallow import Schema, fields

class EntitySchema(Schema):
    entity_type_name = fields.String(load_from="entityTypeName")
    entity_name = fields.String(load_from="entityName")