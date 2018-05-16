#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging.config

from gevent.server import DatagramServer
import redis
from maple.task import Task
from maple.contrib.virtual_request import VirtualRequest
from maple import Trigger
from maple import constants as maple_constants

from .rate_limiter import RateLimiter
from .blocker import Blocker
from .redis_extend import RedisExtend
from ..utils import import_string
from ..log import logger
from .. import constants


class Server(object):
    test = None

    key_prefix = None

    unauthed_conn_req_max_rate = None
    authed_conn_req_max_rate = None

    ip_conn_create_max_rate = None

    rate_unlimited_ip_list = None

    ip_block_age = None

    box_class = None

    rds_extend = None
    rate_limiter = None
    blocker = None

    trigger = None

    def __init__(self, config=None):
        """
        :param config:
            KEY_PREFIX: maple_guard:app:

            REDIS_URL: redis://127.0.0.1:6379/0

            TEST: False

            BOX_CLASS: netkit.box.Box

            TRIGGER_HOST: 127.0.0.1
            TRIGGER_PORT: 28001

            UNAUTHED_CONN_REQ_MAX_RATE: [(-1, 10),(-1, 60)]
            AUTHED_CONN_REQ_MAX_RATE:

            IP_CONN_CREATE_MAX_RATE:

            RATE_UNLIMITED_IP_LIST: ['127.0.0.1','192.168.1.1']

            IP_BLOCK_AGE: 3600
        :return:
        """
        if hasattr(config, 'LOGGING'):
            logging.config.dictConfig(config.LOGGING)

        self.test = getattr(config, 'TEST', False)
        self.key_prefix = getattr(config, 'KEY_PREFIX', None) or constants.KEY_PREFIX
        self.unauthed_conn_req_max_rate = getattr(config, 'UNAUTHED_CONN_REQ_MAX_RATE', None)
        self.authed_conn_req_max_rate = getattr(config, 'AUTHED_CONN_REQ_MAX_RATE', None)
        self.ip_conn_create_max_rate = getattr(config, 'IP_CONN_CREATE_MAX_RATE', None)
        self.rate_unlimited_ip_list = getattr(config, 'RATE_UNLIMITED_IP_LIST', None)
        self.ip_block_age = getattr(config, 'IP_BLOCK_AGE', -1)

        rds = redis.from_url(config.REDIS_URL)
        self.rds_extend = RedisExtend(rds)

        self.box_class = import_string(
            getattr(config, 'BOX_CLASS', constants.BOX_CLASS)
        )
        self.trigger = Trigger(self.box_class,
                               config.TRIGGER_HOST,
                               config.TRIGGER_PORT,
                               False
                               )

        self.rate_limiter = RateLimiter(self.rds_extend)
        self.blocker = Blocker(rds)

    def handle_message(self, message, address):
        task = Task()
        ret = task.unpack(message)

        if ret <= 0:
            # 因为对于udp来说，是可以保证message是完整的，除非调用方就没有发完整
            logger.error('unpack fail. ret: %d, message: %r', ret, message)
            return

        if task.cmd not in (maple_constants.CMD_CLIENT_REQ, maple_constants.CMD_CLIENT_CREATED):
            logger.info('invalid cmd. task: %r', task)
            return

        if self._is_rate_unlimited_ip(task):
            return

        if self._is_ip_blocked(task):
            # 处理就好
            logger.info('ip blocked. task: %r, ip: %s', task, task.client_ip)
            self._punish_client(task)
            return

        if task.cmd == maple_constants.CMD_CLIENT_CREATED:
            limited_values = self._is_ip_conn_create_limit(task)
            if limited_values:
                logger.error('connection create rate limited. task: %r, ip: %s, limited_values: %s',
                             task, task.client_ip, limited_values)
                self._block_ip(task)
                self._punish_client(task)
                return
        elif task.cmd == maple_constants.CMD_CLIENT_REQ:
            limited_values = self._is_conn_req_limit(task)
            if limited_values:
                logger.error('connection req rate limited. task: %r, ip: %s, limited_values: %s',
                             task, task.client_ip, limited_values)
                self._block_ip(task)
                self._punish_client(task)
                return

    def _is_conn_req_limit(self, task):
        key = constants.CONN_LIMIT_KEY_TPL.format(
            prefix=self.key_prefix,
            node_id=task.node_id,
            tag=task.tag,
            conn_id=task.conn_id,
            status=1 if task.uid else 0,
        )

        max_rate = self.authed_conn_req_max_rate if task.uid else self.unauthed_conn_req_max_rate

        return self.rate_limiter.hit(key, max_rate)

    def _is_ip_conn_create_limit(self, task):
        key = constants.IP_LIMIT_KEY_TPL.format(
            prefix=self.key_prefix,
            node_id=task.node_id,
            ip=task.client_ip,
        )

        max_rate = self.ip_conn_create_max_rate

        return self.rate_limiter.hit(key, max_rate)

    def _is_rate_unlimited_ip(self, task):
        """
        是否无限制IP
        :param task:
        :return:
        """

        return self.rate_unlimited_ip_list and task.client_ip in self.rate_unlimited_ip_list

    def _is_ip_blocked(self, task):
        """
        是否被封
        :param task:
        :return:
        """

        key = constants.IP_BLOCK_KEY_TPL.format(
            prefix=self.key_prefix,
            node_id=task.node_id,
            ip=task.client_ip,
        )

        return self.blocker.is_blocked(key)

    def _block_ip(self, task):
        """
        封IP
        :param task:
        :return:
        """

        key = constants.IP_BLOCK_KEY_TPL.format(
            prefix=self.key_prefix,
            node_id=task.node_id,
            ip=task.client_ip,
        )

        return self.blocker.block(key, self.ip_block_age)

    def _punish_client(self, task):
        """
        惩罚client
        清除掉client的所有tasks
        踢掉client
        :return:
        """
        if self.test:
            # 如果是test模式，就不做处理
            return

        request = VirtualRequest(task, self.trigger)
        request.clear_client_tasks()
        request.close_client()

    def run(self, host, port):
        class UDPServer(DatagramServer):
            def handle(sub_self, message, address):
                try:
                    self.handle_message(message, address)
                except:
                    logger.error('exc occur. message: %r, address: %s', message, address, exc_info=True)

        logger.info("running on %s:%s", host, port)

        server = UDPServer((host, port))

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        except:
            logger.error('exc occur.', exc_info=True)
