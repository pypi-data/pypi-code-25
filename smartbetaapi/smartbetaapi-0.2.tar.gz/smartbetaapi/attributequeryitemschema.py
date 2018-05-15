from marshmallow import Schema, fields, post_load
from .attributetypeschema import AttributeTypeSchema

class AttributeQueryItemSchema(Schema):
    query_item_key = fields.String(load_from="queryItemKey")
    item_type = fields.String(load_from="itemTypeName")
    data_provider_name = fields.String(load_from="dataProviderName")
    data_feed_name = fields.String(load_from="dataFeedName")
    attribute_type = fields.Nested(AttributeTypeSchema, load_from="attributeType")