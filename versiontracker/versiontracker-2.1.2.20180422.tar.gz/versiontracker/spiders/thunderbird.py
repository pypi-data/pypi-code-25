import re

from scrapy import Request

from . import Spider
from .xpath import XPath


class Thunderbird(Spider):
    name = 'thunderbird'
    file_url_pattern = 'https://download\\.mozilla\\.org/\\?product=' \
                       'thunderbird-(\\d+(?:\\.\\d+)+)-SSL&.*$'

    def parse(self, response):
        xpath = '//a[re:test(@href, \'{}\')]/@href'
        version = re.match(self.file_url_pattern, xpath.format(
            self.file_url_pattern)).group(1)
        response.meta['version'] = version
        url = "https://ftp.mozilla.org/pub/thunderbird/releases/" \
              "{}/source/".format(version)
        response.meta['url'] = url
        response.meta['response'] = response
        filename = "thunderbird-{}.source.tar.xz".format(version)
        return Request(url + filename, callback=self.parse_file_server,
                       meta=response.meta, method='HEAD')

    @staticmethod
    def parse_file_server(response):
        return XPath.parse_date_from_header(response)

    def first_request(self, data):
        return 'https://www.mozilla.org/en-US/thunderbird/all/'
