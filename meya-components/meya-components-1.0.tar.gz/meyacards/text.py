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


class TextWithButtons(CardWithButtons):
    type = "text_buttons"

    class Schema(CardWithButtons.Schema):
        text = fields.Str(required=True, validate=validate.Length(max=2000))

    def __init__(self, payload=None, **kwargs):
        super(TextWithButtons, self).__init__(payload=payload, **kwargs)
        self.text = self.payload.get('text')

    def as_text(self):
        strs = [self.text, self.buttons_to_text]
        return " ".join(filter(None, strs))
