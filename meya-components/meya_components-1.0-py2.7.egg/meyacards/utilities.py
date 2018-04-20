# -*- coding: UTF-8 -*-
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

import re


IMAGE_REGEX = r"""https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+˜#=]{2,256}
    \.[a-z]{2,6}\/[-a-zA-Z0-9@:%_\+\(\).~#?&\/\/=]+\b(png|gif|jpg)
    \b([\?][-a-zA-Z0-9@:%_\+\(\).~#?&\/\/=]*)?"""


def get_image_type(image_url):
    img_regex = re.compile(IMAGE_REGEX, re.VERBOSE)

    match = img_regex.search(image_url)

    image_type = None
    if match:
        try:
            image_type = match.groups(1)[1]
        except Exception:
            image_type = None

    return image_type


def has_sentence_ender(str):
    return str.endswith(('.', '!', '?'))


def turn_into_sentences(string_array):
    _results = []
    for s in string_array:
        if s:
            if not has_sentence_ender(s):
                s += '.'
            _results.append(s)

    return " ".join(_results)
