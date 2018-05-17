# WatchGhost, your invisible but loud monitoring pet
# Copyright © 2015 Kozea

import json
import logging
import os
import shutil
from collections import OrderedDict
from os.path import abspath, dirname, isdir
from uuid import uuid4

import asyncssh
from tornado.options import options

from . import app
from .loggers import Logger
from .services import Service
from .watchers import Watcher

logger = logging.getLogger(__name__)

app.servers = OrderedDict()
app.services = OrderedDict()
app.watchers = OrderedDict()
app.loggers = []


class Server:
    '''
    A Server is only represented by its name. This name is a string that must
    be unique amongst all servers and groups.

    Any other pair of key/value can be configured.

    Example:

    .. code-block:: json

      {
        "jupiter": {
          "ipv4": "100.10.10.10",
          "ipv6": "2001:db8:100:0:bda1:1c51:c598:6ef8"
        },
        "ceres": {
          "ipv4": "100.10.10.11",
          "ipv6": "2001:db8:100:0:2df2:b059:4067:437e"
        },
        "vulcan": {
          "ipv4": "100.10.10.12",
          "ipv6": "2001:db8:100:0:eccf:6af2:e2:9e"
        }
      }
    '''
    def __init__(self, name, config):
        self.uuid = uuid4().hex
        self.name = name
        self.config = config
        self.watchers = []
        self._ssh = None

    def __getattr__(self, name):
        return self.config[name]

    async def ssh_command(self, command, reentry=False):
        if not self._ssh:
            self._ssh = await asyncssh.connect(
                self.config.get('ipv4'),
                port=int(self.config.get('ssh_port', 22)),
                username=self.config.get('ssh_username'),
                password=self.config.get('ssh_password'),
                client_keys=self.config.get('ssh_client_keys', ()),
                passphrase=self.config.get('ssh_passphrase'),
            )
        try:
            return await self._ssh.create_process(command)
        except asyncssh.misc.ChannelOpenError:
            if reentry:
                raise
            self._ssh = None
            return await self.ssh_command(command, reentry=True)


def read():
    if not isdir(options.config):
        conf_src = os.path.join(dirname(abspath(__file__)), 'etc')
        shutil.copytree(conf_src, options.config)

    servers = json.load(
        open(os.path.join(options.config, 'servers')),
        object_pairs_hook=OrderedDict)
    for server, config in servers.items():
        app.servers[server] = Server(server, config)

    server_groups = {}
    groups = json.load(
        open(os.path.join(options.config, 'groups')),
        object_pairs_hook=OrderedDict)
    for group, servers in groups.items():
        server_groups[group] = [app.servers[server] for server in servers]

    loggers = json.load(
        open(os.path.join(options.config, 'loggers')),
        object_pairs_hook=OrderedDict)
    for logger in loggers:
        app.loggers.append(Logger(logger))

    watchers = json.load(
        open(os.path.join(options.config, 'watchers')),
        object_pairs_hook=OrderedDict)
    for config in watchers:
        service_name = config['service']
        if not config.get('enabled', True):
            continue
        service = Service(service_name)
        app.services[service_name] = service
        if 'group' in config:
            servers = server_groups[config['group']]
        elif 'server' in config:
            servers = (app.servers[config['server']],)
        else:
            assert False, (
                'watcher is not attached to a group or a host %r' % config
            )

        app.watchers.setdefault(service_name, [])
        for server in servers:
            # TODO: filter loggers according to server and service
            app.watchers[service_name].append(
                Watcher(server, service, config, app.loggers)
            )
