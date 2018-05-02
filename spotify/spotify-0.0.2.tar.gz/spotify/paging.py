##
# -*- coding: utf-8 -*-
##
from .http import Route

class PagingObject:
    __slots__ = ['_client', '_history', '_items', '_ctx']

    def __init__(self, client, data):
        self._client = client
        self._history = []
        self._items = []
        self._ctx = {'previous': data['previous'], 'next': data['next'], 'limit': data['limit'], 'total': data['total']}

        self._history.append(data['href'])
        self._items.append([])
        for _object in data['items']:
            self._items[-1].append(client._construct(_object, _object.get('type')))

    async def fetch_next(self):
        if self._ctx['previous'] is None:
            self._ctx['previous'] = False
            return self._items[0]

        elif self._ctx['next'] is None:
            return None

        path = '/' + self._ctx['next'].split('/', maxsplit=4)[-1]
        route = Route('GET', path)

        data = await self._client.http.request(route)
        self._ctx = {'previous': data['previous'], 'next': data['next'], 'limit': data['limit'], 'total': data['total']}

        self._history.append(data['href'])
        self._items.append([])

        for _object in data['items']:
            self._items[-1].append(self._client._construct(_object, _object.get('type')))

    def __repr__(self):
        return '<spotify.PagingObject: (total=%s, pages=%s)>' %(self._ctx['total'], int(self._ctx['total']) // int(self._ctx['limit']))

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def __aiter__(self):
        return self

    async def __anext__(self):
        data = await self.fetch_next()
        if data is not None:
            return data
        else:
            raise StopAsyncIteration
