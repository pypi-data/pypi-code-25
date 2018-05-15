from marshmallow import Schema, fields, post_load
from .attributetypeschema import AttributeTypeSchema

class AttributeQueryItemSchema(Schema):
    query_item_key = fields.String(data_key="queryItemKey")
    item_type = fields.String(data_key="itemTypeName")
    data_provider_name = fields.String(data_key="dataProviderName")
    data_feed_name = fields.String(data_key="dataFeedName")
    attribute_type = fields.Nested(AttributeTypeSchema, data_key="attributeType")