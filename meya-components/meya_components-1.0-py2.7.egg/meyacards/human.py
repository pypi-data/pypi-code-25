# Copyright 2018 Locl Interactive Inc. (d/b/a Meya.ai). All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from marshmallow import fields, validate
from meyacards.base import Card


class Agent(Card):
    def as_text(self):
        return ""

    class Schema(Card.Schema):
        title = None


class Transfer(Agent):
    """Bot transfers control to a human agent"""
    type = "transfer"

    class Schema(Agent.Schema):
        confirm = fields.Boolean(required=False, allow_none=True)
        priority = fields.Integer(required=False, allow_none=True)
        requester = fields.Str(required=False, allow_none=True, default="bot")

    def __init__(self, payload=None, **kwargs):
        super(Transfer, self).__init__(payload=payload, **kwargs)
        self.confirm = self.payload.get('confirm')
        self.priority = self.payload.get('priority')
        self.requester = self.payload.get('requester')


class Takeover(Agent):
    """Bot takes control from any human agent"""
    type = "takeover"


class Note(Agent):
    """Bot leaves a note for the human agent to read"""
    type = "note"

    class Schema(Agent.Schema):
        text = fields.Str(required=True, validate=validate.Length(max=5120))

    def __init__(self, payload=None, **kwargs):
        super(Note, self).__init__(payload=payload, **kwargs)
        self.text = self.payload.get('text')


class Close(Agent):
    """Bot can close conversation/ticket"""
    type = "close"
