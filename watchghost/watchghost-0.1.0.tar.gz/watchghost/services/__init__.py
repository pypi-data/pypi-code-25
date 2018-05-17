# WatchGhost, your invisible but loud monitoring pet
# Copyright © 2015 Kozea

from collections import OrderedDict
from importlib import import_module
from uuid import uuid4

import logging

logger = logging.getLogger(__name__)


class Service:
    """A Service is responsible for checking something.

    A Watcher is a Service applied to a server or a group, with custom
    attributes.

    Any watcher must have the following attributes:

    - service: the service class name.
    - server or group: the server name or group name.

    Any watcher can have the following attributes:

    - description: a string representing the watcher (default: None).
    - repeat: the time period between two checks, in seconds (default: 3600).
    - after: the hour when the checks must start (default: "00:00:00").
    - before: the hour when the checks must stop (default: "23:59:59").
    - retry: the number of checks giving the same result before declaring the
      state as hard (default: 2).
    - retry_interval: the time period (in seconds), between two checks when the
      state is not hard (default: 15).
    - status: a mapping between statuses and filters that trigger these
      statuses.

    Example:

    .. code-block:: json

      [
        {
          "service": "network.Ping",
          "group": "postgres",
          "description": "Ping IPv4",
          "ip_version": 4
        },
        {
          "service": "network.HTTP",
          "server": "ceres",
          "description": "HTTP",
          "url": "http://test.org:8888/",
          "status": {"warning": [{"code": 404}]}
        }
      ]

    This example defines two watchers. The first one pings the IPv4 of the
    postgres group's servers. The second one fetches the
    "http://test.org:8888/" page on the "ceres" server and gives a warning
    status when the status code is 404 (otherwise gives what the HTTP watcher's
    default config does).

    """

    config = {
        'description': None,
        'repeat': 3600,
        'before': '23:59:59',
        'after': '00:00:00',
        'status': OrderedDict([
            ('info', [{'ok': True}]),
            ('critical', [{}])
        ]),
        'retry': 2,
        'retry_interval': 15,
    }

    def __init__(self, name):
        self.uuid = uuid4().hex
        self.name = name

        module_name, service_name = name.rsplit('.', 1)
        module = import_module('watchghost.services.{}'.format(module_name))
        self.cls = getattr(module, service_name)

        self.config = self.config.copy()
        self.config.update(self.cls.config)

        self.description = self.config['description']

    async def check(self, server, config):
        """Check the service and return the status.

        :return: A dictionary with various values corresponding to the status
            of the service. The default keys included in the dict are 'ok'
            (True if the service works, else False) and 'message' (a string
            describing the status).

        """
        try:
            response = await self.cls.check(server, config)
        except Exception as exception:
            logger.exception('exception occured in service')
            return {
                'ok': False,
                'message': 'An internal error occured: {}'.format(exception)}
        else:
            if 'ok' not in response:
                response['ok'] = False
            if 'message' not in response:
                response['message'] = 'No message'
            return response
