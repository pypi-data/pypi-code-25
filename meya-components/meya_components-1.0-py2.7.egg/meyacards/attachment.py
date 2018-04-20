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
from meyacards.base import Card


class Attachment(Card):
    type = None     # implemented in inherited class

    class Schema(Card.Schema):
        url = fields.Url(required=True)

    def __init__(self, payload=None, **kwargs):
        super(Attachment, self).__init__(payload=payload, **kwargs)
        self.url = self.payload.get('url')

    def as_text(self):
        return self.url


class Video(Attachment):
    type = "video"


class Audio(Attachment):
    type = "audio"


class File(Attachment):
    type = "file"
