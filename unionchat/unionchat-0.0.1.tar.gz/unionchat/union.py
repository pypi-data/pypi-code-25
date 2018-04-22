import websockets
import json
import base64
import asyncio
from pyee import EventEmitter


class SelfUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class Server:
    def __init__(self, data):
        self.name = data['name']
        self.id = data['id']
        self.messages = []

    #async def createMessage(self, message):

class Message:
    def __init__(self, client, msg):
        self.client = client
        self.server = self.client.servers[msg['server']]
        self.content = msg['content']
        self.author = msg['author']
        self.id = msg['id']
        self.createdAt = msg['createdAt']
        if self.author == self.client.user.username:
            self.self = self.author

    async def reply(self, content):
        await self.client.createMessage(self.server.id, content)

    async def delete(self):
        if self.author != self.client.user.username:
            raise CannotDeleteOtherMessages('You can not delete a message that was not sent by you!')
        await self.client.deleteMessage(self.id)


class Client:
    def __init__(self, username, password):
        if not username:
            raise UsernameMustExist('options.username must exist and may not be null')
        if not password:
            raise PasswordMustExist('options.password must exist and may not be null')
        self.user = SelfUser(username, password)
        self.ready = False
        self.servers = {}
        self._ws = None
        self.ee = EventEmitter()

    async def _connect(self):
        if self._ws:
            self._ws.terminate()
        encodedAuth = base64.b64encode(bytes(('{username}:{password}'.format(username=self.user.username, password=self.user.password)).encode('utf-8')))
        headers = {'Authorization': 'Basic {}'.format(encodedAuth.decode('utf-8'))}
        self._ws = await websockets.connect('wss://union.serux.pro:2096', extra_headers=headers, loop=self.loop)
        while True:
            try:
                payload = await asyncio.wait_for(self._ws.recv(), timeout=3600)
                self._handlePayload(payload)
            except asyncio.TimeoutError:
                #TODO: Implement reconnecting or shit
                pass



    def start(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self._connect())

    async def createMessage(self, server, content):
        if not self.ready:
            raise NotReadyYet('Client is not ready yet!')
        payload = json.dumps({'op': 8, 'd': {'server': server, 'content': content}})
        await self._ws.send(payload)

    async def deleteMessage(self, id):
        if not self.ready:
            raise NotReadyYet('Client is not ready yet!')
        payload = json.dumps({'op': 10, 'd': id})
        await self._ws.send(payload)

    def _handlePayload(self, payload):
        payload = json.loads(payload)
        if payload['op'] == 1:
            self.ready = True
            for server in payload['d']:
                self.servers[server['id']] = Server(server)
            self.ee.emit('ready')
        if payload['op'] == 3:
            message = Message(self, payload['d'])
            self.servers[payload['d']['server']].messages.append(message)
            self.ee.emit('message', message)
        if payload['op'] == 6:
            self.ee.emit('message_delete', payload['d'])
        if payload['op'] == 11:
            self.ee.emit('bad_request', payload['d'])
        if payload['op'] == 5:
            self.ee.emit('member_join', payload['d'])
        if payload['op'] == 4:
            id = payload['d']['id']
            status = payload['d']['status']
            self.ee.emit('presence_change', id, status)



class CannotDeleteOtherMessages(Exception):
    def __init__(self, message):
        self.message = message


class UsernameMustExist(Exception):
    def __init__(self, message):
        self.message = message


class PasswordMustExist(Exception):
    def __init__(self, message):
        self.message = message

class NotReadyYet(Exception):
    def __init__(self, message):
        self.message = message