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

from meyastore.base import BaseDB
from meyastore.list import ListDB


class LoggingDB(BaseDB):
    table = 'logging-2'
    partition_key = 'account_id'
    sort_key = 'log_id'

    def __init__(self, account_id, log_id):
        '''Instantiate a new log.'''
        # We set 'bot_id' to None, as it is not used in our key.
        # It may still be present in our data.
        super(LoggingDB, self).__init__(None)
        self.account_id = account_id
        self.item_id = log_id


class LoggingListDB(ListDB):
    table = 'logging-2'
    partition_key = 'account_id'
    sort_key = 'log_id'

    def __init__(self, account_id):
        '''Instantiate a new log list interface.'''
        # We set 'bot_id' to None, as it is not used in our key.
        # It may still be present in our data.
        super(LoggingListDB, self).__init__(None)
        self.account_id = account_id
