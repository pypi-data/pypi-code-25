import asyncio


class LogGenerator:
    def __init__(self, cont, loop=None):
        self.container = cont
        self.logs = self.container.logs(stream=True)
        self.loop = loop or asyncio.get_event_loop()
        self.i = 0
        self.reading = False

    def __aiter__(self):
        self.reading = True

        return self

    def _read_line_async(self):
        try:
            value = next(self.logs)
            value = bytes([x for x in value if int(x) >= 32])
            return value
        except StopIteration:
            self.reading = False
            return None

    async def __anext__(self):
        await asyncio.sleep(0)

        # reading from logs is long blocking operation

        value = await self.loop.run_in_executor(None, self._read_line_async)

        if self.reading:
            return value
        else:
            raise StopAsyncIteration
