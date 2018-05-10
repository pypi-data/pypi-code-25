import asyncio
import tempfile
import os.path

import asynctest
import msgpack

import aiomsgpack


class TestRead(asynctest.TestCase):

    async def test_basic(self):
        proto = aiomsgpack.MsgpackProtocol(None)
        proto.data_received(msgpack.packb(1))
        proto.data_received(msgpack.packb(2))

        self.assertEqual(await proto.read(), 1)
        self.assertEqual(await proto.read(), 2)

    async def test_eof(self):
        proto = aiomsgpack.MsgpackProtocol(None)
        proto.data_received(msgpack.packb(1))
        proto.eof_received()

        self.assertEqual(await proto.read(), 1)
        with self.assertRaises(StopAsyncIteration):
            await proto.__anext__()

        self.assertEqual(await proto.read(), None)

    async def test_partial(self):
        proto = aiomsgpack.MsgpackProtocol(None)
        msg = msgpack.packb(b'hello world')
        proto.data_received(msg[:5])  # Send partial message

        fut = asyncio.ensure_future(proto.__anext__())
        await asyncio.sleep(0.1)  # Yield to event loop
        self.assertFalse(fut.done())

        proto.data_received(msg[5:])  # Send remainder of message

        self.assertEqual(await fut, b'hello world')


class TestClientServer(asynctest.TestCase):

    async def test(self):

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, 'socket')

            server_proto_fut = asyncio.Future()

            async def server_connected_cb(proto):
                server_proto_fut.set_result(proto)

            async def client_connected_cb(proto):
                pass

            loop = asyncio.get_event_loop()

            server = await loop.create_unix_server(
                aiomsgpack.make_msgpack_protocol_factory(server_connected_cb),
                path
            )
            _, client_proto = await loop.create_unix_connection(
                aiomsgpack.make_msgpack_protocol_factory(client_connected_cb),
                path
            )
            server_proto = await server_proto_fut
            try:
                server_proto.write(b'hello')
                self.assertEqual(await client_proto.read(), b'hello')

                client_proto.write(b'hi')
                self.assertEqual(await server_proto.read(), b'hi')

            finally:
                client_proto.close()
                server_proto.close()
                server.close()
                await server.wait_closed()


