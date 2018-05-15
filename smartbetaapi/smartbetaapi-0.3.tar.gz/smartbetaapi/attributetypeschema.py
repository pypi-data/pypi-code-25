from marshmallow import Schema, fields, post_load

class AttributeTypeSchema(Schema):
    attribute_type_id = fields.Integer(data_key="attributeTypeId")
    attribute_type_name = fields.String(data_key="attributeTypeName")
    attribute_classification_id = fields.Integer(data_key="attributeClassificationId")
    hierarchy_id = fields.Integer(data_key="hierarchyId")
