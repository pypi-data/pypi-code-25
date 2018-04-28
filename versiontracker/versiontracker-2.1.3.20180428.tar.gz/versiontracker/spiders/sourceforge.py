import re

from scrapy import Request

from ..items import Item

from . import value_from_match, PathSpider


LATEST_LINK_XPATH = '//a[re:test(@href, \'.*latest/download\\?source=files$\')]'
LATEST_RE = re.compile(r"^(?P<path>.*):\s+released\s+on\s+(?P<date>.*)$")


class UndefinedLatestFile(Exception):
    pass


class SourceForge(PathSpider):
    name = 'sourceforge'

    def first_request(self, data):
        data['base_url'] = 'http://sourceforge.net/projects/{}/files'.format(
            data.get('project', data['id']))
        if data['path'].endswith("}") and not data['path'].count('/'):
            return Request(
                'http://sourceforge.net/projects/{}/files'.format(
                    data.get('package', data['id'])),
                meta=data, callback=self.parse_latest)
        return super().first_request(data)

    def iter_entries(self, response):
        for tr in response.xpath('//table[@id=\'files_list\']//tbody//tr'
                                 '[not(re:test(@class, \'\\bempty\\b\'))]'):
            yield {'date': tr.xpath('.//td[1]//abbr/@title').extract_first(),
                   'name': tr.xpath('./@title').extract_first()}

    def parse_latest(self, response):
        try:
            link_selector = response.xpath(LATEST_LINK_XPATH)
            if not link_selector:
                raise UndefinedLatestFile
            match = LATEST_RE.match(
                link_selector.xpath('./@title').extract_first())
            if not match:
                raise UndefinedLatestFile
            path_parts = match.group('path').split('/')
            date = match.group('date')
            name = path_parts[-1]
            name_pattern = ':'.join(response.meta['path'][:-1].split(":")[1:])
            match = re.search(name_pattern, name)
            if not match:
                raise UndefinedLatestFile
            return Item(version=value_from_match(match), date=date,
                        response=response)
        except UndefinedLatestFile:
            return super().first_request(response.meta)

    def path_url(self, data):
        return data['base_url'] + data['new_path']
