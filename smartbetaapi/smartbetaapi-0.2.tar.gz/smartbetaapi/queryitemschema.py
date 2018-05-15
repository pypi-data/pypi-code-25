from marshmallow import Schema, fields, post_load


class QueryItemSchema(Schema):
    query_item_key = fields.String(load_from="queryItemKey")
    item_type = fields.String(load_from="itemTypeName")
    data_feed_name = fields.String(load_from="dataFeedName")
    data_provider_name = fields.String(load_from="dataProviderName")
