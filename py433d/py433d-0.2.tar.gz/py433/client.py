from socket import (
    AF_INET,
    SOCK_STREAM,
    socket
)

from . import defaults


class client():

    def __init__(self, host='localhost', port=defaults.port):
        self.host = host
        self.port = port

    def send(self, message='hello'):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        try:
            self.sock.sendall(message.encode('utf-8'))
        finally:
            self.sock.close()
