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

from meyastore import (
    BotDB, UserDB, UserListDB, RequestDB, RequestListDB, TableDB)


class MeyaDB(object):
    """Bundle of Meya datastore objects with 3 scopes: `bot`, `user`,
    `request`. Each datastore supports:
        - put(data)
        - update(data)
        - set(key, value)
        - get(key)
        - get_all()
        - delete()
    """

    def __init__(self, bot_id, user_id, request_id):
        self.bot_id = bot_id
        self.bot = BotDB(bot_id)
        self.user = UserDB(bot_id, user_id)
        self.users = UserListDB(bot_id)
        self.flow = RequestDB(bot_id, request_id)
        self.flows = RequestListDB(bot_id)
        # for backwards compability
        self.request = self.flow

    def table(self, namespace):
        return TableDB(self.bot_id, namespace)
