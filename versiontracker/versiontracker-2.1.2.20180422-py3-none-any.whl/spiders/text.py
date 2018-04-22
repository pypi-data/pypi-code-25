from chardet import detect

from ..items import Item

from . import Spider


class Text(Spider):
    name = 'text'

    def parse(self, response):
        text = response.body.decode(detect(response.body)['encoding'])
        return Item(date=text if not response.meta['no-date'] else None,
                    response=response,
                    version=text)

    def start_requests(self):
        return super().iter_start_requests(
            params={'no-date': False})

    def first_request(self, data):
        return data['url']
