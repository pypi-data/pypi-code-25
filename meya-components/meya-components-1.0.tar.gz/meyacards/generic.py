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
from meyacards.utilities import get_image_type, turn_into_sentences
from meyacards.base import Card, CardWithButtons
from meyacards.controls.buttons import Button


class Generic(CardWithButtons):
    type = "generic"

    class Schema(CardWithButtons.Schema):
        text = fields.Str(
            required=False, validate=validate.Length(max=1024))
        image_url = fields.Url(required=False, allow_none=True)
        item_url = fields.Url(allow_none=True, required=False)
        buttons = fields.Nested(Button.Schema, required=False, many=True)

    def __init__(self, payload=None, **kwargs):
        super(Generic, self).__init__(payload=payload, **kwargs)
        self.text = self.payload.get('text')
        self.image_url = self.payload.get('image_url')
        self.item_url = self.payload.get('item_url')
        self._image_type = self.payload.get('image_type')

    @property
    def image_type(self):
        if not self._image_type and self.image_url:
            self._image_type = get_image_type(self.image_url)

        return self._image_type

    def as_text(self):
        strs = [self.title_text, self.item_url,
                self.image_url, self.buttons_to_text]
        return " ".join(filter(None, strs))

    @property
    def title_text(self):
        return turn_into_sentences([self.title, self.text])


class GenericMultiSchema(Generic.Schema):
    type = fields.Str(required=False, validate=validate.Length(max=20))


class GenericMulti(Card):
    type = "generic_multi"

    class Schema(Card.Schema):
        elements = fields.Nested(
            GenericMultiSchema, required=True, many=True)

    def __init__(self, payload=None, elements=None, **kwargs):
        # pre-process if elements are passed in directly
        # support: a) elements as dict, b) elements as objects
        if elements:
            _elements = []
            for e in elements:
                # elements are passed in as objects, so convert to dict
                if type(e) is Generic:
                    _buttons = []
                    for button in e.buttons:
                        if type(button) is Button:
                            # convert nested button as dict
                            _buttons.append(button.payload)
                        else:
                            _buttons.append(button)
                    _element_data = e.payload
                    _element_data['buttons'] = _buttons
                    _elements.append(_element_data)
                else:
                    _elements.append(e)
            kwargs['elements'] = _elements

        # call base constructor
        super(GenericMulti, self).__init__(payload=payload, **kwargs)

        # instantiate elements
        self.elements = []
        for element_data in self.payload.get('elements'):
            self.elements.append(Generic(payload=element_data))

    def as_text(self):
        _strs = []
        for el in self.elements:
            _strs.append(el.as_text())
        return " | ".join(_strs)
