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


class ButtonTypes:
    TRANSITION = 'transition'
    LINK = 'link'
    START = 'start'
    ACCOUNT_LINK = 'account_link'
    ACCOUNT_UNLINK = 'account_unlink'
    SHARE = 'share'
    LOCATION = 'location'
    BUY = 'buy'


URL_REGEX = "^([a-z]([a-z]|\d|\+|-|\.)*)://[^\s/$.?#].[^\s]*$"


class Button(object):
    class Schema(Schema):
        webview_height_ratio_error = ("This must be either: "
                                      "compact, tall or full")

        text = fields.Str(
            required=False, allow_none=True,
            validate=validate.Length(max=280))
        description = fields.Str(
            required=False, allow_none=True,
            validate=validate.Length(max=280))
        action = fields.Str(
            required=False, allow_none=True,
            validate=validate.Length(max=280))
        type = fields.Str(
            required=False, allow_none=True, validate=validate.Length(max=50))
        url = fields.Str(
            required=False, allow_none=True,
            validate=[
                validate.Length(max=2048),
                validate.Regexp(regex=URL_REGEX)
            ])
        flow = fields.Str(
            required=False, allow_none=True,
            validate=validate.Length(max=100))
        data = fields.Dict(required=False, allow_none=True)
        webview_height_ratio = fields.Str(
            required=False, allow_none=True,
            validate=[validate.OneOf(choices=['compact', 'tall', 'full'],
                                     error=webview_height_ratio_error)])
        image_url = fields.Str(
            required=False, allow_none=True,
            validate=[
                validate.Length(max=2048),
                validate.Regexp(regex=URL_REGEX)
            ])
        messenger_extensions = fields.Bool(required=False, allow_none=True)
        fallback_url = fields.Str(
            required=False, allow_none=True,
            validate=[
                validate.Length(max=2048),
                validate.Regexp(regex=URL_REGEX)
            ])

    def __init__(self, payload=None, **kwargs):
        payload = payload or kwargs

        # infer the type
        if 'type' not in payload:
            if payload.get('url'):
                payload['type'] = ButtonTypes.LINK
            elif payload.get('flow'):
                payload['type'] = ButtonTypes.START
            else:
                payload['type'] = ButtonTypes.TRANSITION

        # action defaults to text
        account_link_types = (
            ButtonTypes.ACCOUNT_LINK, ButtonTypes.ACCOUNT_UNLINK)

        if payload.get('action') is None:
            if payload['type'] == ButtonTypes.TRANSITION:
                payload['action'] = payload.get('text')
            elif payload['type'] in account_link_types:
                payload['action'] = payload['type']

        if payload.get('text') is None:
            if payload['type'] == ButtonTypes.ACCOUNT_LINK:
                payload['text'] = "Log in"
            elif payload['type'] == ButtonTypes.ACCOUNT_UNLINK:
                payload['text'] = "Log out"
            elif payload['type'] == ButtonTypes.SHARE:
                payload['text'] = "Share"
            elif payload['type'] == ButtonTypes.LOCATION:
                payload['text'] = "Send Location"
            elif payload['type'] == ButtonTypes.LINK:
                # Due to Messenger's default action which doesn't require text
                pass
            else:
                raise Exception("`text` is a required field.")

        result = self.Schema().load(payload)
        assert result.errors == {}, "Invalid buttons data. {}".format(
            result.errors)

        self._output_data = result.data

        # add any "additional" payload data
        for key in payload:
            if key not in self._output_data:
                self._output_data[key] = payload[key]

        self.text = self._output_data.get('text', "")
        self.description = self._output_data.get('description', "")
        self.url = self._output_data.get('url', None)
        self.flow = self._output_data.get('flow', None)
        self.action = self._output_data.get('action', None)
        self.data = self._output_data.get('data', None)
        self.type = self._output_data.get('type', None)
        self.webview_height_ratio = self._output_data.get(
            'webview_height_ratio', None)
        self.image_url = self._output_data.get('image_url', None)
        self.messenger_extensions = self._output_data.get(
            'messenger_extensions', None)
        self.fallback_url = self._output_data.get('fallback_url', None)

    @property
    def payload(self):
        return self._output_data

    @property
    def as_text(self):
        return "[{}]".format(self.action)


class Suggestion(Button):

    def __init__(self, payload=None, **kwargs):
        # Suggestion is a subset of a button that only accepts text
        payload = payload or kwargs
        super(Suggestion, self).__init__(text=payload.get('text'))
