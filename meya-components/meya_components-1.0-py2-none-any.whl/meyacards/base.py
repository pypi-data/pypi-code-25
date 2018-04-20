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

from marshmallow import Schema, fields, validate
from meyacards.controls.buttons import Button


class Card(object):
    type = None

    class Schema(Schema):
        type = fields.Str(required=True, validate=validate.Length(max=20))
        title = fields.Str(
            required=False, allow_none=True, validate=validate.Length(max=128))

    def __init__(self, payload=None, **kwargs):
        # instantiate from dict or kwargs
        payload = payload or kwargs

        # set the type if it's not already set inside the payload
        if not payload.get("type"):
            payload.update({'type': self.type})

        # check the inputs
        schema = self.Schema()
        result = schema.load(payload)
        assert result.errors == {}, "Invalid card data. {}".format(
            result.errors)

        # add the serialized data
        self._output_data = schema.dump(result.data).data

        # add any "additional" payload data
        for key in payload:
            val = payload[key]
            if type(val) in (list, dict) or key not in self._output_data:
                self._output_data[key] = val

        self.title = self.payload.get('title')

    def has_buttons(self):
        return False

    def as_text(self):
        return ""

    @property
    def payload(self):
        return self._output_data


class CardWithButtons(Card):

    class MODES:
        DEFAULT = "default"
        QUICK_REPLY = "quick_reply"
        BUTTON = "button"

    class Schema(Card.Schema):
        buttons = fields.Nested(Button.Schema, required=True, many=True)
        mode = fields.Str(
            required=False, allow_none=True, validate=validate.Length(max=20))

    def __init__(self, payload=None, buttons=None, **kwargs):
        self.buttons = []
        if buttons:
            # buttons are passed in as objects to pass as dict to base
            self.buttons = buttons
            kwargs['buttons'] = [b.payload for b in buttons]

        super(CardWithButtons, self).__init__(payload=payload, **kwargs)
        self.mode = self.payload.get('mode') or CardWithButtons.MODES.DEFAULT

        # instantiate the buttons
        if not self.buttons:
            _buttons = self.payload.get('buttons', [])
            for b in _buttons:
                self.buttons.append(Button(b))

    def has_buttons(self):
        if self.buttons:
            return True
        return False

    @property
    def buttons_to_text(self):
        _buttons = []
        for button in self.buttons:
            _buttons.append("[{}]".format(button.action))
        return " ".join(_buttons)
