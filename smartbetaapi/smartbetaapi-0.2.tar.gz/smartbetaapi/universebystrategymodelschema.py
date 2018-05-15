from marshmallow import Schema, fields


class UniverseByStrategyModelSchema(Schema):
    _active_date = fields.Date(dump_to="activeDate", format="%Y-%m-%d", allow_none=False)
    _entity_ids = fields.Dict(dump_to="entityIds")
    _strategy = fields.String(dump_to="strategy")
