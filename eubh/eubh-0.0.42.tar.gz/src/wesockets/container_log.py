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
        print("Web Socket Opened .")
        try:
            if len(self.client.containers.list()) > 0:
                for container in self.client.containers.list():
                    for line in container.logs(stream=True):
                        print(dumps({
                            'type': 'eubh',
                            'project_machine_id': self.pivot.get('id'),
                            'data': line
                        }))
                        self.send(dumps({
                            'type': 'eubh',
                            'project_machine_id': self.pivot.get('id'),
                            'data': line
                        }))
            else:
                self.close()
        except:
            self.close()
            self.connect()
            print("Web socket is close . ")
