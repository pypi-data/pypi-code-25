import websockets
import json
import base64
import asyncio
import aiohttp
from pyee import EventEmitter
from collections import OrderedDict


class SelfUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class Server:
    def __init__(self, data):
        self.name = data['name']
        self.id = data['id']
        self.messages = []
        self.icon_url = data['iconUrl']
        self.members = OrderedDict()

    def get_member(self, id):
        self.get_member_info(self.id, id)


class Member:
    def __init__(self, data):
        try:
            self.avatar_url = data['avatarUrl']
        except KeyError:
            self.avatar_url = 'https://union.serux.pro/default_avatar.png'
        self.created_at = data['createdAt']
        self.status = data['online']
        self.name = data['id']

    def __str__(self):
        return self.name

    def mention(self):
        return '@{}'.format(self.name)


class Message:
    def __init__(self, client, msg):
        self.client = client
        self.server = self.client.servers[msg['server']]
        self.content = msg['content']
        self.author = self.server.members[msg['author']]
        self.id = msg['id']
        self.createdAt = msg['createdAt']
        if self.author == self.client.user.username:
            self.self = self.author

    def __str__(self):
        return self.content

    async def reply(self, content):
        message = await self.client.create_message(self.server.id, content)
        return message

    async def send(self, content):
        await self.reply(content)

    async def delete(self):
        if self.author != self.client.user.username:
            raise CannotDeleteOtherMessages('You can not delete a message that was not sent by you!')
        await self.client.delete_message(self.id)


class Client:
    def __init__(self, username, password, **kwargs):
        if not username:
            raise UsernameMustExist('options.username must exist and may not be null')
        if not password:
            raise PasswordMustExist('options.password must exist and may not be null')
        self.user = SelfUser(username, password)
        self.ready = False
        self.servers = {}
        self._ws = None
        self.event = EventEmitter()
        self.message_cache = OrderedDict()
        self.cache_size = kwargs.get('cache_size')
        self.loop = kwargs.get('loop')
        if self.loop is None:
            self.loop = asyncio.get_event_loop()
        self.api = aiohttp.ClientSession(loop=self.loop)
        if self.cache_size is None or self.cache_size < 100:
            self.cache_size = 500

    async def _connect(self):
        if self._ws:
            self._ws.terminate()
        self.encodedAuth = base64.b64encode(bytes(('{username}:{password}'.format(username=self.user.username, password=self.user.password)).encode('utf-8')))
        headers = {'Authorization': 'Basic {}'.format(self.encodedAuth.decode('utf-8'))}
        self._ws = await websockets.connect('wss://union.serux.pro:2096', extra_headers=headers, loop=self.loop)
        while True:
            try:
                payload = await asyncio.wait_for(self._ws.recv(), timeout=3600)
                self._handle_payload(payload)
            except asyncio.TimeoutError:
                #TODO: Implement reconnecting or shit
                pass

    def start(self):
        self.loop.run_until_complete(self._connect())

    async def send_message(self, server, content):
        await self.create_message(server, content)

    async def create_message(self, server, content):
        if not self.ready:
            raise NotReadyYet('Client is not ready yet!')
        payload = json.dumps({'op': 8, 'd': {'server': server, 'content': content}})
        headers = {'Authorization': 'Basic {}, content-type: application/json'.format(self.encodedAuth.decode('utf-8'))}
        data = {'server': server, 'content': content}
        async with self.api.post('https://union.serux.pro/api/message', headers=headers, data=data) as r:
            if r.status != 200:
                await self._ws.send(payload)
                await asyncio.sleep(1)
                messages = list(self.message_cache.items())
                for k in messages[-1]:
                    return self.message_cache[k]
            else:
                try:
                    response = await r.json()
                    message = Message(self, response['d'])
                    return message
                except aiohttp.client_exceptions.ContentTypeError:
                    await self._ws.send(payload)
                    await asyncio.sleep(1)
                    messages = list(self.message_cache.items())
                    for k in messages[-1]:
                        return self.message_cache[k]

    async def delete_message(self, id):
        if not self.ready:
            raise NotReadyYet('Client is not ready yet!')
        payload = json.dumps({'op': 10, 'd': id})
        await self._ws.send(payload)

    def get_message(self, id):
        if not self.ready:
            raise NotReadyYet('Client is not ready yet!')
        try:
            return self.message_cache[id]
        except KeyError:
            return

    def get_member_info(self, server, id):
        if not self.ready:
            raise NotReadyYet('Client is not ready yet!')
        try:
            return self.servers[server].members[id]
        except:
            return

    def _handle_payload(self, payload):
        payload = json.loads(payload)
        if payload['op'] == 1:
            self.ready = True
            for server in payload['d']:
                self.servers[server['id']] = Server(server)
            get_server = self.servers[server['id']]
            for member in server['members']:
                get_server.members[member['id']] = Member(member)
            self.event.emit('ready')
        if payload['op'] == 3:
            message = Message(self, payload['d'])
            if len(self.message_cache) > self.cache_size:
                messages = list(self.message_cache.keys())
                self.message_cache.pop(messages[1])
            self.servers[payload['d']['server']].messages.append(message)
            self.message_cache[payload['d']['id']] = Message(self, payload['d'])
            self.event.emit('message', message)
        if payload['op'] == 6:
            message = self.message_cache[payload['d']]
            self.event.emit('message_delete', message)
        if payload['op'] == 11:
            self.event.emit('bad_request', payload['d'])
        if payload['op'] == 5:
            print(payload['d'])
            get_server = self.servers[1]
            get_server.members[payload['d']] = Member(payload['d'])
            self.event.emit('member_join', payload['d'])
        if payload['op'] == 4:
            id = payload['d']['id']
            status = payload['d']['status']
            self.event.emit('presence_change', id, status)


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