from typing import Dict, List, NewType

from urllib.parse import parse_qs

import httptools

QueryDict = NewType('QueryDict', Dict[str, List[str]])


class Request:
    def __init__(self):
        self.method: str = ''
        self.path: str = ''
        self.headers = {}
        self.handler = None

        self.GET: QueryDict = {}
        self.POST = {}

    def parse_url(self, url: bytes) -> None:
        parsed_url = httptools.parse_url(url)
        self.path = parsed_url.path.decode()

        query_params = parsed_url.query
        if query_params:
            self.GET.update(parse_qs(query_params.decode()))

    async def handle(self):
        response = await self.handler()
        return response
