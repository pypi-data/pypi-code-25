from marshmallow import Schema, fields
from marshmallow_enum import EnumField


class MembershipFilterSchema(Schema):
    _identifier = fields.String(data_key="identifier")
