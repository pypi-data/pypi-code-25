import re

from scrapy import Request

from ..items import Item

from . import Spider


class OpenBSD(Spider):
    name = 'openbsd'

    def parse(self, response):
        xpath = '//table//tr/td[2]//a[re:test(@href, \'^\\d+\\.html$\')]/@href'
        return Request(response.urljoin(response.xpath(xpath).extract_first()),
                       callback=self.parse_announcement,
                       meta=response.meta)

    def parse_announcement(self, response):
        xpath = '//h2//text()'
        version = ' '.join(response.xpath(xpath).extract()).strip().split()[-1]
        date = re.search("\nReleased (.*)<br>", response.text).group(1)
        return Item(date=date, response=response, version=version)

    def first_request(self, data):
        return 'http://www.openbsd.org/'
