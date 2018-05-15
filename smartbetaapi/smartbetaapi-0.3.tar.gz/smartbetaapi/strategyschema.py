from marshmallow import Schema, fields, post_load


class StrategySchema(Schema):
    strategy_id = fields.Integer(data_key="strategyId")
    strategy_name = fields.String(data_key="strategyName")
