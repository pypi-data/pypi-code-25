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

class MeyaCMS(object):
    """Interface to Meya Bot CMS"""

    def __init__(self, bot_id, user_id, request_id):
        self.bot_id = bot_id
        self.user_id = user_id
        self.request_id = request_id

    def languages(self):
        raise Exception("Feature not available in local testing!")

    def get(self, space, key, languages=None):
        raise Exception("Feature not available in local testing!")
