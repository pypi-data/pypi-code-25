import asyncio, json, websockets
import rovcontrol.drivers.com.ComTemp as ComTemp

class WsCom(ComTemp.ComTemp):
    async def handle_con(self, ws, p):
        while True:
            command = await ws.recv()
            command = json.loads(command)
            if command['op'] == "get":
                x = self.getr(command['device'], command['register'], command['channel'])
                command.update({'value' : x})
                await ws.send(json.dumps(command))
            if command['op'] == "set":
                self.setr(command['device'], command['register'], command['value'], command['channel'])

    def listen(self):
        asyncio.get_event_loop().run_until_complete(websockets.serve(self.handle_con, '0.0.0.0', 8765))
        asyncio.get_event_loop().run_forever()
