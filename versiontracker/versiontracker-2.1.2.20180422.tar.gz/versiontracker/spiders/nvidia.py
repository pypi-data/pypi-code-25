from scrapy import Request

from ..items import Item

from . import Spider


class NVidia(Spider):
    name = 'nvidia'

    def parse(self, response):
        return Request(
            response.xpath(
                '//text()[re:test(., \'Latest Short Lived Branch version:\')]/'
                'following-sibling::a/@href').extract_first(),
            callback=self.parse_details,
            meta=response.meta)

    @staticmethod
    def parse_details(response):
        date = response.xpath(
            '//td[@id=\'tdReleaseDate\']/text()').extract_first()
        version = response.xpath(
            '//td[@id=\'tdVersion\']/text()').extract_first().strip()
        return Item(date=date, response=response, version=version)

    def first_request(self, data):
        return 'http://www.nvidia.com/object/unix.html'
