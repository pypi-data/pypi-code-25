import re

from scrapy import Request

from ..items import Item

from . import Spider


class Apt(Spider):
    name = 'apt'

    _URL = 'https://tracker.debian.org/pkg/apt'

    def parse(self, response):
        version = response.xpath('//a[@href=\'https://packages.debian.org/'
                                 'source/stable/apt\']/text()').extract_first()
        response.meta['url'] = self._URL
        response.meta['version'] = version
        yield Request(
            'https://tracker.debian.org/media/packages/a/apt/changelog-' +
            version, meta=response.meta, callback=self.parse_date)

    @staticmethod
    def parse_date(response):
        date = re.search(r'(?m)--[^<]*<[^>]*>\s*(.*)$', response.text).group(1)
        yield Item(date=date, response=response)

    def first_request(self, data):
        return self._URL
