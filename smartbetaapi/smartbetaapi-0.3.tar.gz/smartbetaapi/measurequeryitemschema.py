from marshmallow import Schema, fields, post_load
from .measureschema import MeasureSchema

class MeasureQueryItemSchema(Schema):
    query_item_key = fields.String(data_key="queryItemKey")
    item_type = fields.String(data_key="itemTypeName")
    measure_name = fields.Nested(MeasureSchema, only=['measure_name'], data_key="measure")
    data_provider_name = fields.String(data_key="dataProviderName")
    data_feed_name = fields.String(data_key="dataFeedName")
