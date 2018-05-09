from __future__ import absolute_import

import logging
import time
from random import randrange

from celery import states as celery_states
from celery.signals import task_prerun, task_postrun, worker_process_init

from slogging import SLoggerHandler

from threading import local


class CeleryTaskSLoggerHandler(SLoggerHandler):
    TASK_STATE_TO_STATUS_CODE = {
        celery_states.SUCCESS: 200,
        celery_states.FAILURE: 500
    }

    def __init__(self, **kwargs):
        super(CeleryTaskSLoggerHandler, self).__init__(**kwargs)
        self._current_tasks_info = {}
        self._task_local = local()

    def install(self):
        task_prerun.connect(self.__before_task)
        task_postrun.connect(self.__after_task)
        worker_process_init.connect(self.__setup_logging)

    def _logline(self, *args, **kwargs):
        if 'severity_no' in kwargs and hasattr(self._task_local, 'log_severity_no'):
            self._task_local.log_severity_no = max(self._task_local.log_severity_no, kwargs['severity_no'])
        if 'request_id' not in kwargs:
            kwargs['request_id'] = getattr(self._task_local, 'fake_request_id', None)
        super(CeleryTaskSLoggerHandler, self)._logline(*args, **kwargs)

    def _generate_random_request_id(self, task_id):
        return 'celery@{}_{}.{:x}#{:x}'.format(
            self.backend_name,
            task_id,
            int(time.time() * 1000), randrange(0xffffffff + 1)
        )

    def __setup_logging(self, **kwargs):
        super(CeleryTaskSLoggerHandler, self).install()

    def __before_task(self, sender, task_id, task, **kwargs):
        self._task_local.fake_request_id = self._generate_random_request_id(task_id)
        self._task_local.task_id = task_id
        self._task_local.log_severity_no = logging.NOTSET

        fake_url = '/__celery_tasks__/{}'.format(task.name.replace('.', '/'))
        self._request_start(
            request_id=self._task_local.fake_request_id,
            ip='0.1.0.2',
            url=fake_url, method='POST',
            host='celery'
        )
        self.set_request_custom(
            request_id=self._task_local.fake_request_id,
            custom={
                'celery_task_id': task_id,
                'celery_task_name': task.name,
                'celery_task_retry': task.request.retries,
                'celery_task_parent_id': task.request.parent_id,
                'celery_task_root_id': task.request.root_id,
                'celery_task_utc': task.request.utc
            }
        )

    def __after_task(self, sender, state, **kwargs):
        self._request_finish(
            request_id=self._task_local.fake_request_id,
            status_code=self.TASK_STATE_TO_STATUS_CODE.get(state, 999),
            log_severity=self._task_local.log_severity_no
        )
        self._task_local.fake_request_id = None
        self._task_local.task_id = None
        self._task_local.log_severity_no = None
