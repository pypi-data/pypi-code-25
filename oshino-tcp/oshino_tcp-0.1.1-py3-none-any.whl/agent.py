import socket
import select
import re

from oshino import Agent

from oshino_tcp import dynamic_load


def print_out(msg):
    print(msg)


class AsyncSocketWrapper(object):
    ADDR_PATT = re.compile(r"(tcp://)?(?P<host>\w+):(?P<port>\d+)")

    def __init__(self, chunk_size=1024):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(0)
        self.chunk_size = chunk_size
        self.connections = [self._socket]

    @classmethod
    def parse_addr(cls, addr):
        result = cls.ADDR_PATT.search(addr)
        return result.group("host"), int(result.group("port"))

    def bind(self, addr):
        return self._socket.bind(self.parse_addr(addr))

    def connect(self, addr):
        return self._socket.connect(self.parse_addr(addr))

    def listen(self, size=1):
        return self._socket.listen(size)

    def accept(self):
        conn, _ = self._socket.accept()
        self.connections.append(conn)

    def recv(self):
        return self._socket.recv(self.chunk_size)

    def open_for_read(self):
        read, write, error = select.select(self.connections,
                                           [],
                                           [],
                                           0.01)

        if self._socket in read:
            self.accept()

        return filter(lambda x: x != self._socket, read)


class TCPAgent(Agent):

    @property
    def bind(self):
        return self._data.get("bind", None)

    @property
    def connect(self):
        return self._data["connect"]

    @property
    def parser(self):
        path = self._data.get("parser", None)
        if path:
            return dynamic_load(path)
        else:
            return None

    def _parse(self, msg):
        parser_fn = self.parser
        if parser_fn:
            return parser_fn(msg)
        else:
            return None

    async def process(self, event_fn):
        logger = self.get_logger()
        if self.socket_active:
            try:
                logger.trace("Waiting for connection")
                sockets = self.socket.open_for_read()
                logger.trace("Available connections: {0}"
                             .format(len(sockets)))
                logger.trace("Trying to read msg")
                for r in sockets:
                    try:
                        msg = r.recv(1024)
                    except:
                        logger.trace("Disconnect received")
                        self.socket.connections.remove(r)
                        r.close()
                        continue

                    logger.trace("Received msg: '{0}'".format(msg))
                    msg_obj = self._parse(msg)
                    if msg_obj:
                        event_fn(service=self.prefix, **msg_obj)
            except BlockingIOError:
                logger.trace("Nothing interesting is happening")
            except Exception as ex:
                logger.exception(ex)
        else:
            logger.debug("TCP socket is still waiting for connection")

    def on_start(self):
        logger = self.get_logger()
        logger.info("Initializing TCP Socket")
        self.socket = AsyncSocketWrapper()
        if self.bind:
            self.socket.bind(self.bind)
            logger.info("TCP Socket bound on: {0}".format(self.bind))
            self.socket_active = True
        else:
            self.socket.connect(self.connect)
            logger.info("TCP Socket connected to: {0}".format(self.connect))
            self.socket_active = True
        self.socket.listen(1)

    def on_stop(self):
        self.socket.close()
