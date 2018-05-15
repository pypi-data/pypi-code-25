from marshmallow import Schema, fields, post_load


class StrategySchema(Schema):
    strategy_id = fields.Integer(load_from="strategyId")
    strategy_name = fields.String(load_from="strategyName")
