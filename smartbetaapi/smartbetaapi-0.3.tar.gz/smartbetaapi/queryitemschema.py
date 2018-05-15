from marshmallow import Schema, fields, post_load


class QueryItemSchema(Schema):
    query_item_key = fields.String(data_key="queryItemKey")
    item_type = fields.String(data_key="itemTypeName")
    data_feed_name = fields.String(data_key="dataFeedName")
    data_provider_name = fields.String(data_key="dataProviderName")
