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

"""Implements worker metrics.

"""

####################################################################################################

from .Statistics import DataSetMoment
from .Units import to_MB

####################################################################################################

class WorkerMetrics:

    ##############################################

    def __init__(self, worker_id):

        self._worker_id = worker_id
        self._crash = 0
        self._timeout = 0
        self._restart = 0
        self._memory = DataSetMoment()
        self._task_time = DataSetMoment()

    ##############################################

    def register_crash(self):
        self._crash += 1

    ##############################################

    def register_timeout(self):
        self._timeout += 1

    ##############################################

    def register_restart(self):
        self._restart += 1

    ##############################################

    def register_memory(self, memory):

        self._memory.fill(memory)

    ##############################################

    def register_task_time(self, task_time):

        # if worker_id not in self._task_time:
        #     self._task_time[worker_id] = DataSetMoment()

        self._task_time.fill(task_time)

    ##############################################

    def dump_statistics(self):

        template = '''
Worker @{0._worker_id}: {0._task_time.number_of_entries} Tasks
  number of crashs: {0._crash}
  number of timeout: {0._timeout}
  number of restarts: {0._restart}
'''
        text = template.format(self)
        if self._memory:
            avg_memory = to_MB(self._memory.mean)
            text += '  avg memory: {:.1f} MB\n'.format(avg_memory)
        if self._task_time:
            text += '  avg task time: {0._task_time.mean:.3f}s\n'.format(self)

        return text
