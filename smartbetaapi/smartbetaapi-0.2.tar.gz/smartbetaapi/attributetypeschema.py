from marshmallow import Schema, fields, post_load

class AttributeTypeSchema(Schema):
    attribute_type_id = fields.Integer(load_from="attributeTypeId")
    attribute_type_name = fields.String(load_from="attributeTypeName")
    attribute_classification_id = fields.Integer(load_from="attributeClassificationId")
    hierarchy_id = fields.Integer(load_from="hierarchyId")
