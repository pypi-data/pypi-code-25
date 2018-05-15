from marshmallow import Schema, fields


class UniverseQueryItemModelSchema(Schema):
    _active_date = fields.Date(dump_to="activeDate", format="%Y-%m-%d")
    _entity_ids = fields.Dict(dump_to="entityIds")
    _query_items = fields.Dict(dump_to="queryItems")
