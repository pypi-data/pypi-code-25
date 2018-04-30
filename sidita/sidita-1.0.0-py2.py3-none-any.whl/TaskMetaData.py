####################################################################################################
#
# sidita - Simple Distributed Task Queue
# Copyright (C) 2018 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

"""Implements a class to store task metadata.

"""

####################################################################################################

__all__ = [
    'TaskMetaData',
    'TaskState',
]

####################################################################################################

from datetime import datetime
from enum import Enum

####################################################################################################

class TaskState(Enum):

    SUBMITTED = 0
    DISPATCHED = 1
    READY = 2
    TIMEOUT = 3
    CRASHED = 4

####################################################################################################

class TaskMetaData:

    __LAST_TASK_ID__ = -1

    ##############################################

    @classmethod
    def new_tak_id(cls):

        cls.__LAST_TASK_ID__ += 1
        return cls.__LAST_TASK_ID__

    ##############################################

    def __init__(self, task):

        self._task = task
        self._id = self.new_tak_id()
        self._state = TaskState.SUBMITTED
        self._result = None

        self._woker_id = None
        self._submitted_date = datetime.now()
        self._dispatch_date = None
        self._result_date = None

    ##############################################

    @property
    def task(self):
        return self._task

    @property
    def id(self):
        return self._id

    @property
    def state(self):
        return self._state

    @property
    def result(self):
        return self._result

    @property
    def worker_id(self):
        return self._worker_id

    @property
    def submitted_date(self):
        return self._submitted_date

    @property
    def dispatch_date(self):
        return self._submitted_date

    @property
    def result_date(self):
        return self._submitted_date

    @property
    def task_time(self):
        return self._result_date - self._dispatch_date

    @property
    def task_time_s(self):
        return (self._result_date - self._dispatch_date).total_seconds()

    ##############################################

    def dispatch(self, worker_id):

        self._worker_id = worker_id
        self._dispatch_date = datetime.now()
        self._state = TaskState.DISPATCHED

    ##############################################

    def _set_result(self, state, value=None):

        self._state = state
        self._result = value
        self._result_date = datetime.now()

    ##############################################

    @result.setter
    def result(self, value):
        self._set_result(TaskState.READY, value)

    ##############################################

    def set_timeout(self):
        self._set_result(TaskState.TIMEOUT)

    ##############################################

    def set_crashed(self):
        self._set_result(TaskState.CRASHED)
