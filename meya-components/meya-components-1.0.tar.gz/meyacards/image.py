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

from marshmallow import fields
from meyacards.base import Card, CardWithButtons
from meyacards.utilities import get_image_type


class Image(Card):
    type = "image"

    class Schema(Card.Schema):
        image_url = fields.Url(required=True)

    def __init__(self, payload=None, **kwargs):
        super(Image, self).__init__(payload=payload, **kwargs)
        self.image_url = self.payload.get('image_url')
        self._image_type = self.payload.get('image_type')

    @property
    def image_type(self):
        if not self._image_type and self.image_url:
            self._image_type = get_image_type(self.image_url)

        return self._image_type

    def as_text(self):
        return self.image_url


class ImageWithButtons(CardWithButtons):
    type = "image_buttons"

    class Schema(CardWithButtons.Schema):
        image_url = fields.Url(required=True)

    def __init__(self, payload=None, **kwargs):
        super(ImageWithButtons, self).__init__(payload=payload, **kwargs)
        self.image_url = self.payload.get('image_url')
        self.image_type = self.payload.get('image_type')

    def as_text(self):
        strs = [self.image_url, self.buttons_to_text]
        return " ".join(filter(None, strs))
