from marshmallow import Schema, fields


class UniverseQueryItemModelSchema(Schema):
    _active_date = fields.Date(data_key="activeDate", format="%Y-%m-%d")
    _entity_ids = fields.Dict(data_key="entityIds")
    _query_items = fields.Dict(data_key="queryItems")
