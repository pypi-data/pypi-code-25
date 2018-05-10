import functools
import asyncio

import msgpack


def make_msgpack_protocol_factory(client_connected_cb, unpacker_args={}, packer_args={}, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    return functools.partial(MsgpackProtocol, client_connected_cb, unpacker_args, packer_args, loop=loop)


class MsgpackProtocol (asyncio.Protocol):
    def __init__(self, client_connected_cb, unpacker_args={}, packer_args={}, loop=None):
        self._client_connected_cb = client_connected_cb
        self._unpacker = msgpack.Unpacker(**unpacker_args)
        self._packer = msgpack.Packer(**packer_args)
        self._more_data_event = asyncio.Event()
        self._eof = False
        self._exc = None
        self._transport = None
        self._loop = loop

    def connection_made(self, transport):
        self._transport = transport
        self._loop.create_task(self._client_connected_cb(self))

    def connection_lost(self, exc):
        self._exc = exc

    def data_received(self, data):
        self._unpacker.feed(data)
        self._more_data_event.set()

    def eof_received(self):
        self._eof = True
        self._more_data_event.set()

    def __aiter__(self):
        return self

    async def __anext__(self):
        while True:
            try:
                return self._unpacker.unpack()
            except msgpack.OutOfData:
                pass
            if self._exc:
                raise self._exc
            if self._eof:
                raise StopAsyncIteration()
            self._more_data_event.clear()
            await self._more_data_event.wait()

    async def read(self):
        try:
            return await self.__anext__()
        except StopAsyncIteration:
            return None

    @property
    def transport(self):
        return self._transport

    def write(self, obj):
        self._transport.write(self._packer.pack(obj))

    def write_eof(self):
        return self._transport.write_eof()

    def can_write_eof(self):
        return self._transport.can_write_eof()

    def close(self):
        return self._transport.close()

    def get_extra_info(self, name, default=None):
        return self._transport.get_extra_info(name, default)
