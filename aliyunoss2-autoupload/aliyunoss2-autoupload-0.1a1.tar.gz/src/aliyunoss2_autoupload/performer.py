#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, with_statement, print_function, generators

import concurrent.futures
import os
import sys
from glob import iglob
from shutil import move
from time import time

import oss2
from oss2.exceptions import OssError

from . import glb
from .utils.loggermixin import LoggerMixin

try:
    import crcmod._crcfunext
except ImportError as err:
    _crc = False
    print('{0}. CRC will be DISABLED'.format(err), file=sys.stderr)
else:
    _crc = True

__all__ = ['Performer']


class Performer(LoggerMixin):
    _executor = None  # type: concurrent.futures.Executor

    @classmethod
    def initial(cls):
        max_workers = glb.config['watcher'].get('max_workers')
        cls._executor = concurrent.futures.ThreadPoolExecutor(max_workers)

    @classmethod
    def release(cls):
        cls._executor.shutdown()

    @classmethod
    def run_once(cls):
        logger = cls.get_logger()
        logger.debug('run_once() >>>')

        now_ts = time()
        tasks = []  # type: List[Task]

        for path in iglob(glb.config['watcher']['patterns'], recursive=bool(glb.config['watcher']['recursive'])):
            # is file write completed? (According to last modify time)
            mod_ts = os.path.getmtime(path)
            if now_ts - mod_ts > glb.config['watcher']['write_complete_time']:
                task = Task(path)
                tasks.append(Task(path))
                cls.get_logger().info('run_once(): add task: %r', task)

        cls._executor.map(cls._execute_task, tasks)

        logger.debug('run_once() <<<')

    @classmethod
    def _execute_task(cls, task):  # type: (Task) -> None
        logger = cls.get_logger()
        logger.debug('execute_task(%r) >>>', task)
        try:
            bucket = cls._get_oss_bucket()
            try:
                logger.info(
                    'execute_task(): upload %s => %s',
                    task.path, task.oss_key
                )
                bucket.put_object_from_file(task.oss_key, task.path)
            except OssError as e:
                logger.exception(
                    'execute_task(): put_object_from_file %s => %s. OssError: %s',
                    task.path, task.oss_key, e
                )
            try:
                logger.info(
                    'execute_task(): backup %s => %s',
                    task.path, task.bak_path
                )
                move(task.path, task.bak_path)
            except OSError as e:
                logger.exception(
                    'execute_task(): backup %s => %s. OSError: %s',
                    task.path, task.bak_path, e
                )
        except Exception:
            logger.exception('execute_task(%r)', task)
            raise
        finally:
            logger.debug('execute_task(%r) <<<', task)

    @classmethod
    def _get_oss_bucket(cls):
        cfg = glb.config['oss']
        auth = oss2.Auth(cfg['access_key_id'], cfg['access_key_secret'])
        is_cname = bool(cfg['cname'])
        bucket = oss2.Bucket(
            auth, cfg['endpoint'], cfg['name'], is_cname=is_cname, enable_crc=_crc
        )
        return bucket


class Task(object):

    def __init__(self, path):
        self._path = path
        self._oss_key = ''
        self._bak_path = ''

        rel_dir = glb.config['dir']['rel_dir']
        if rel_dir:
            rel_path = os.path.relpath(path, rel_dir)
        else:
            rel_path = os.path.relpath(path)
        self._bak_path = os.path.join(glb.config['dir']['bak_dir'], rel_path)
        upload_path = os.path.normpath(rel_path)
        upload_dir = glb.config['dir']['oss_dir']
        if upload_dir:
            self._oss_key = '/'.join((upload_dir, upload_path))
        else:
            self._oss_key = upload_dir

    @property
    def path(self):
        return self._path

    @property
    def oss_key(self):
        return self._oss_key

    @property
    def bak_path(self):
        return self._bak_path

    def __repr__(self):
        rep = super(Task, self).__repr__()
        return '{0}(path={1}, oss_key={2}, bak_path={3})'.format(
            rep, self.path, self.oss_key, self.bak_path)
