from marshmallow import Schema, fields


class UniverseByStrategyModelSchema(Schema):
    _active_date = fields.Date(data_key="activeDate", format="%Y-%m-%d", allow_none=False)
    _entity_ids = fields.Dict(data_key="entityIds")
    _strategy = fields.String(data_key="strategy")
