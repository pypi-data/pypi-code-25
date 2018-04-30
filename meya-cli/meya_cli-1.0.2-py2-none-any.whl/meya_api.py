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

from __future__ import print_function
from __future__ import absolute_import

import re

import os
import requests

from meya_cli.meya_config import REST_API_VERSION, USER_AGENT_STRING


class MeyaAPIException(Exception):
    PATTERN = re.compile(".*")
    MESSAGE = None

    @classmethod
    def raise_if_match(cls, error):
        for error in error:
            if cls.PATTERN.match(error):
                raise cls(cls.MESSAGE or error)


class MeyaNoSuchFileException(MeyaAPIException):
    PATTERN = re.compile("No such.*file.*")


class MeyaFileTooBigException(MeyaAPIException):
    PATTERN = re.compile(".*Ensure this field has no more "
                         "than .* characters.*")


class MeyaInvalidAPIKey(MeyaAPIException):
    PATTERN = re.compile(".*Invalid API key.*")
    MESSAGE = "The API key you are trying to use is invalid. " \
              "Please check the API key of the bot you " \
              "intend to use on its Settings page."


class MeyaVersionUnsupported(MeyaAPIException):
    PATTERN = re.compile(".*API version.*exceeds.*")

    def __init__(self, message):
        super(MeyaVersionUnsupported, self).__init__(
            "Server reported: " + message + "\nmeya-cli is out of date. " +
            "Please run 'pip install --upgrade meya-cli'."
        )


ERROR_TYPES = [
    MeyaNoSuchFileException,
    MeyaFileTooBigException,
    MeyaInvalidAPIKey,
    MeyaVersionUnsupported,
    # generic error:
    MeyaAPIException
]


def raise_error(response):
    errors = []
    try:
        parsed_response = response.json()
        errors = parsed_response.get("errors", [])
        if "detail" in parsed_response:
            errors.append(parsed_response["detail"])
    except ValueError:
        if response.status_code == 404:
            errors = ["Got 404 from '" + response.request.url +
                      "'. This URL format might be incorrect, or an "
                      "incorrect 'api_root' might be set."]
    if not errors:
        errors = [
            "Unexpected server error. Got back: " + response.text
        ]
    for cls in ERROR_TYPES:
        cls.raise_if_match(errors)


class MeyaAPI(object):
    REQUEST_TIMEOUT = 60

    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def _agent_and_version(self, base_json=None):
        json = base_json or {}
        json.update(
            version=REST_API_VERSION,
            user_agent=USER_AGENT_STRING
        )
        return json

    def get(self, path):
        response = requests.get(
            os.path.join(self.base_url, path),
            # Can serve files:
            headers={'content-type': 'application/json'},
            json=self._agent_and_version(),
            auth=(self.api_key, None),
            timeout=self.REQUEST_TIMEOUT
        )
        if response.status_code < 200 or response.status_code >= 300:
            raise_error(response)
        return response.json()

    def post(self, path, data):
        response = requests.post(
            os.path.join(self.base_url, path),
            # Can serve files:
            headers={'content-type': 'application/json'},
            json=self._agent_and_version(data),
            auth=(self.api_key, None),
            timeout=self.REQUEST_TIMEOUT
        )
        if response.status_code < 200 or response.status_code >= 300:
            raise_error(response)
        return response.json()

    def delete(self, path):
        response = requests.delete(
            os.path.join(self.base_url, path),
            # Can serve files:
            headers={'Content-Type': 'application/json'},
            json=self._agent_and_version(),
            auth=(self.api_key, None),
            timeout=self.REQUEST_TIMEOUT
        )
        if response.status_code < 200 or response.status_code >= 300:
            raise_error(response)
        return response.json()
