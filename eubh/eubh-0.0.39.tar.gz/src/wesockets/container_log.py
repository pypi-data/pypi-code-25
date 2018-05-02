from json import dumps

import docker
from ws4py.client.threadedclient import WebSocketClient


class ContainerLog(WebSocketClient):

    def __init__(self, url, pivot, protocols=None, extensions=None, heartbeat_freq=None, ssl_options=None, headers=None,
                 exclude_headers=None):
        super(ContainerLog, self).__init__(url, protocols, extensions, heartbeat_freq, ssl_options, headers,
                                           exclude_headers)
        self.pivot = pivot
        self.client = docker.from_env()

    def opened(self):
        try:
            for container in self.client.containers.list():
                for line in container.logs(stream=True):
                    self.send(dumps({
                        'type': 'eubh',
                        'project_machine_id': self.pivot.get('id'),
                        'data': line
                    }))
        except:
            print("Web socket is close . ")
