from marshmallow import Schema, fields

class EntitySchema(Schema):
    entity_type_name = fields.String(data_key="entityTypeName")
    entity_name = fields.String(data_key="entityName")