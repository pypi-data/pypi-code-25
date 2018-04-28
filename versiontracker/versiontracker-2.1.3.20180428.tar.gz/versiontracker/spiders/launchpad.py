import re

from ..items import Item

from . import Spider


_DATE_RE = re.compile("^(.*?) by.*$")


class Launchpad(Spider):
    name = 'launchpad'

    @staticmethod
    def extract(response, field_name, pattern):
        return re.search(pattern, response.xpath(
            '//div[@id=\'downloads\']//div[re:test(@class, \'\\b{}\\b\')]/'
            'text()'.format(field_name)).extract_first().strip()).group(1)

    def parse(self, response):
        date = self.extract(response, 'released', '^released on (.*)$')
        version = self.extract(response, 'version', '^Latest version is (.*)$')
        return Item(date=date, response=response, version=version)

    def first_request(self, data):
        return 'https://launchpad.net/{}'.format(
            data.get('project', data['id']))
