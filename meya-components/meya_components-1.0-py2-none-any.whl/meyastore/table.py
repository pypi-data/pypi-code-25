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

from meyastore.list import ListDB


class TableDB(ListDB):
    table = 'table'
    sort_key = 'object_id'
    id_prefix = 'O'

    def __init__(self, bot_id, namespace):
        super(TableDB, self).__init__(bot_id)
        self.namespace = namespace

    def get(self, object_id):
        raise Exception("Feature not available in local testing!")

    def filter(self, order_by=None, limit=None, continuation=None, **kwargs):
        raise Exception("Feature not available in local testing!")

    def all(self, order_by=None, limit=None, continuation=None,
            index_name=None, index_key_name=None):
        raise Exception("Feature not available in local testing!")
