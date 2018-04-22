import re

from .xpath import XPath


class Grass(XPath):
    name = 'grass'

    def complete_parsing(self, response):
        item = super().parse_date_from_header(response)
        item['version'] = re.search(
            "\\d+(?:\\.\\d+)+", item['version']).group(0)
        item['url'] = "http://trac.osgeo.org/grass/wiki/Release/{}-News" \
                      "".format(item['version'])
        return item

    def parse(self, response):
        meta = response.meta
        meta.update(XPath.params)
        meta['base'] = ('//a/@href[re:test(., \'^grass\\d+/source/'
                        'grass-\\d+(\\.\\d+)+\\.tar\\.gz$\')]')
        meta['date-url'] = ''
        request = super().parse(response)
        request.callback = self.complete_parsing
        return request

    def first_request(self, data):
        return 'https://grass.osgeo.org/download/software/sources/'
