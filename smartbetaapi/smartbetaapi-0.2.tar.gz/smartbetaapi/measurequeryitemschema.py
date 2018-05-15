from marshmallow import Schema, fields, post_load
from .measureschema import MeasureSchema

class MeasureQueryItemSchema(Schema):
    query_item_key = fields.String(load_from="queryItemKey")
    item_type = fields.String(load_from="itemTypeName")
    measure_name = fields.Nested(MeasureSchema, only=['measure_name'], load_from="measure")
    data_provider_name = fields.String(load_from="dataProviderName")
    data_feed_name = fields.String(load_from="dataFeedName")
