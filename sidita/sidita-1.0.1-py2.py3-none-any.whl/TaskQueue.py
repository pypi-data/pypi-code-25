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

"""Implement a Task Queue using an asyncio event loop and queue.

"""

####################################################################################################

from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import asyncio.subprocess
import logging
import os
import sys

import psutil

from .Message import AsyncMessageStream
from .TaskMetaData import TaskMetaData
from .Units import to_MB
from .WorkerMetrics import WorkerMetrics

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Consumer:

    DEFAULT_WORKER_MAIN = Path(__file__).resolve().parent.joinpath('worker.py')
    DEFAULT_WORKER_MODULE = '.'.join(__name__.split('.')[:-1] + ['Worker']) # Fixme: api tool ?
    DEFAULT_WORKER_CLASS = 'Worker'

    _logger = _module_logger.getChild('Consumer')

    ##############################################

    def __init__(self,
                 worker_id,
                 task_queue,
                 worker_main=DEFAULT_WORKER_MAIN,
                 python_path=None,
                 worker_module=DEFAULT_WORKER_MODULE,
                 worker_cls=DEFAULT_WORKER_CLASS,
                 max_memory=0, # byte
                 memory_check_interval=timedelta(minutes=1),
                 task_timeout=None,
    ):

        self._id = worker_id
        self._task_queue = task_queue
        self._worker_main = worker_main
        self._python_path = python_path
        self._worker_module = worker_module
        self._worker_cls = worker_cls
        self._max_memory = max_memory
        self._memory_check_interval = memory_check_interval
        self._task_timeout = task_timeout

        self._metrics = WorkerMetrics(self._id)
        self._process = None
        self._message_stream = None

    ##############################################

    @property
    def id(self):
        return self._id

    @property
    def metrics(self):
        return self._metrics

    @property
    def dead(self):
        return self._process is None

    ##############################################

    async def run(self):

        last_memory_check = datetime.now()

        while True:
            # await next task
            task_metadata = await self._task_queue.get_task()
            if task_metadata is None:
                break # no more job to process

            # check memory
            if self._max_memory and not self.dead:
                now = datetime.now()
                if now - last_memory_check > self._memory_check_interval:
                    last_memory_check = now
                    process_memory = self._get_process_memory()
                    if process_memory > self._max_memory:
                        self._logger.info('Worker @{} has reached memory limit {:.1f} > {:.1f} MB'.format(
                            self._id, to_MB(process_memory), to_MB(self._max_memory)))
                        await self._stop_worker()

            # check if worker is alive
            # Fixme: does it check for all worker crashes ???
            if self.dead: # process.returncode is not None
                self._logger.info('Restart Worker @{}'.format(self._id))
                await self._create_worker()

            # submit task
            task_metadata.dispatch(self._id)
            self._message_stream.send(task_metadata.task)
            self._task_queue.on_task_sent(task_metadata)

            # await result
            try:
                task_metadata.result = await self._message_stream.receive()
                self._metrics.register_task_time(task_metadata.task_time_s)
                self._task_queue.on_result(task_metadata)
            except asyncio.TimeoutError:
                self._logger.info('Worker @{} timeout'.format(self._id))
                task_metadata.set_timeout()
                self._metrics.register_timeout()
                self._task_queue.on_timeout_error(task_metadata)
                await self._stop_worker()
            except asyncio.streams.IncompleteReadError:
                if self._process.returncode is not None:
                    task_metadata.set_error()
                    self._metrics.register_crash()
                    self._logger.info('Worker @{} is dead'.format(self._id))
                    self._process = None
                self._task_queue.on_stream_error(task_metadata)

        # stop worker
        self._logger.info('Stop worker @{}'.format(self._id))
        if not self.dead:
            await self._stop_worker()

    ##############################################

    async def _stop_worker(self):

        process_memory = self._get_process_memory()
        self._metrics.register_memory(process_memory)
        try:
            self._process.terminate()
            await asyncio.sleep(1) # Fixme: better ?
        except ProcessLookupError: # Fixme:
            self._logger.info('Worker was killed @{} {}'.format(self._id, self._process.returncode))

        self._process = None
        self._message_stream = None

    ##############################################

    def _get_process_memory(self):

        try:
            process_metrics = psutil.Process(self._process.pid)
            with process_metrics.oneshot():
                memory_info = process_metrics.memory_full_info()
                process_memory = memory_info.uss
            return process_memory
        except psutil._exceptions.NoSuchProcess: # Fixme:
            return 0

    ##############################################

    async def _create_worker(self):

        self._logger.info('Create worker @{}'.format(self._id))

        command = [
            sys.executable,
            str(self._worker_main),
            '--worker-module', self._worker_module,
            '--worker-class', self._worker_cls,
            '--worker-id', str(self._id),
            ]
        if self._python_path:
            command += [
                '--python-path', str(self._python_path),
            ]

        self._process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )

        if self._task_timeout is not None:
            timeout = self._task_timeout.total_seconds()
        else:
            timeout = None
        self._message_stream = AsyncMessageStream(
            self._process.stdin,
            self._process.stdout,
            timeout=timeout,
        )

        self._metrics.register_restart()

####################################################################################################

class TaskQueue:

    _logger = _module_logger.getChild('TaskQueue')

    ##############################################

    def __init__(self,
                 number_of_workers=None,
                 max_queue_size=0,
                 **kwargs,
    ):

        self._number_of_workers = number_of_workers or os.cpu_count()
        self._max_queue_size = max_queue_size
        self._consumer_kwargs = kwargs

    ##############################################

    @staticmethod
    def _get_event_loop():

        if sys.platform == 'win32':
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()

        loop.set_debug(True)

        return loop

    ##############################################

    def run(self):

        loop = self._get_event_loop()
        self._queue = asyncio.Queue(maxsize=self._max_queue_size, loop=loop)

        task_producer = self.task_producer()
        task_consumers = [Consumer(i, self, **self._consumer_kwargs)
                          for i in range(self._number_of_workers)]

        loop.run_until_complete(asyncio.gather(
            task_producer,
            *[task_consumer.run() for task_consumer in task_consumers],
        ))
        loop.close()

        for consumer in task_consumers:
            self._logger.info(consumer.metrics.dump_statistics())

    ##############################################

    async def task_producer(self):

        # self.submit(message)
        # self.send_stop()

        raise NotImplementedError

    ##############################################

    async def submit(self, task):

        task_metadata = TaskMetaData(task)
        self.on_task_submitted(task_metadata)
        await self._queue.put(task_metadata)

    ##############################################

    async def send_stop(self):

        # indicate the producer is done
        self._logger.info('Send stop to workers')
        for i in range(self._number_of_workers):
            await self._queue.put(None)

    ##############################################

    async def get_task(self):

        return await self._queue.get()

    ##############################################

    def on_task_submitted(self, task_metadata):

        self._logger.info('Submitted task {0.task}'.format(task_metadata))

    ##############################################

    def on_task_sent(self, task_metadata):

        self._logger.info('Task {0.task} sent to @{0.worker_id}'.format(task_metadata))

    ##############################################

    def on_result(self, task_metadata):

        self._logger.info('Result for task {0.task} from @{0.worker_id}\n{0.result}'.format(task_metadata))

    ##############################################

    def on_timeout_error(self, task_metadata):

        pass

    ##############################################

    def on_stream_error(self, task_metadata):

        pass
