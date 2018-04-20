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
from meyacards.base import CardWithButtons
from meyacards.controls.buttons import Button


class Element(CardWithButtons):
    type = "list_element"

    class Schema(CardWithButtons.Schema):
        title = fields.Str(
            required=True, validate=validate.Length(max=80))
        subtitle = fields.Str(
            required=False, allow_none=True, validate=validate.Length(max=80))
        image_url = fields.Url(required=False, allow_none=True)
        default_action = fields.Nested(
            Button.Schema, required=False, allow_none=True)

        # overrides required in base Schema
        buttons = fields.Nested(Button.Schema, required=False, many=True)

    def __init__(self, payload=None, default_action=None, **kwargs):
        if default_action:
            default_action = default_action.payload if \
                type(default_action) is Button else default_action
        kwargs['default_action'] = default_action

        super(Element, self).__init__(payload=payload, **kwargs)
        self.title = self.payload.get('title')
        self.subtitle = self.payload.get('subtitle')
        self.image_url = self.payload.get('image_url')

        # instantiate default_action
        self.default_action = self.payload.get('default_action', None)
        if self.default_action:
            self.default_action = Button(payload=self.default_action)

    @property
    def as_text(self):
        strs = [self.title, self.subtitle,
                self.image_url, self.default_action_as_text,
                self.buttons_to_text]
        return " ".join(filter(None, strs))

    @property
    def default_action_as_text(self):
        if self.default_action:
            return self.default_action.as_text

        return None


class ListSchema(Element.Schema):
    # NOTE: this is a hack so we can override required field [type]
    # because marshmallow loads does not do nested init to set the type
    type = fields.Str(required=False, validate=validate.Length(max=20))


class List(CardWithButtons):
    type = "list"

    class Schema(CardWithButtons.Schema):
        top_element_style_error = ("This must be either: compact or large")

        top_element_style = fields.Str(
            required=False, allow_none=True,
            validate=[validate.OneOf(choices=['compact', 'large'],
                                     error=top_element_style_error)])
        elements = fields.Nested(ListSchema, many=True, required=True)

        # overrides required in base Schema
        buttons = fields.Nested(Button.Schema, required=False, many=True)

    def __init__(self, payload=None, elements=None, **kwargs):
        # TODO: re-factor, this is a mess
        # pre-process if elements are passed in directly
        # support: a) elements as dict, b) elements as objects
        if elements:
            _elements = []
            for e in elements:
                # elements are passed in as objects, so convert to dict
                if type(e) is Element:
                    _buttons = []
                    for button in e.buttons:
                        if type(button) is Button:
                            # convert nested button as dict
                            _buttons.append(button.payload)
                        else:
                            _buttons.append(button)
                    _element_data = e.payload
                    _element_data['buttons'] = _buttons

                    # default action
                    default_action = e.default_action
                    if default_action:
                        _default_action = default_action.payload if \
                            type(default_action) is Button else default_action
                        _element_data['default_action'] = _default_action
                    _elements.append(_element_data)
                else:
                    _elements.append(e)
            kwargs['elements'] = _elements

        # call base constructor
        super(List, self).__init__(payload=payload, **kwargs)

        # instantiate elements
        self.elements = []
        for element_data in self.payload.get('elements'):
            self.elements.append(Element(payload=element_data))

        self.top_element_style = self.payload.get('top_element_style')

    def as_text(self):
        elements_astext = []
        for el in self.elements:
            elements_astext.append(el.as_text)

        return "{} {}".format(
            " | ".join(elements_astext), self.buttons_to_text)
