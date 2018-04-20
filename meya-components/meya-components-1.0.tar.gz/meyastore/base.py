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

class BaseDB(object):
    # implement in base class
    table = None
    sort_key = None
    partition_key = 'bot_id'
    id_prefix = ''

    def __init__(self, bot_id, item_id=None):
        super(BaseDB, self).__init__()
        # NOTE 'bot_id' is not used in databases where 'account_id' is the
        # partition key
        self.bot_id = bot_id
        self.item_id = item_id

    def put(self, data):
        raise Exception("Feature not available in local testing!")

    def update(self, data):
        raise Exception("Feature not available in local testing!")

    def set(self, key, value):
        raise Exception("Feature not available in local testing!")

    def get(self, key):
        raise Exception("Feature not available in local testing!")

    def all(self):
        raise Exception("Feature not available in local testing!")

    def delete(self):
        raise Exception("Feature not available in local testing!")
