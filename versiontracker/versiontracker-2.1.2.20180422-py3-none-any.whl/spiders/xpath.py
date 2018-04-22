import re

from scrapy import Request

from ..items import Item

from . import Spider


_COMPLETE_XPATH = re.compile(r'.*(@[-_\w]+|text\(\))(\[[^]]+\])*$')


def _xpath(response, field):
    xpath = response.meta[field]
    if xpath is None:
        return None
    xpath = response.meta['base'] + xpath
    if not _COMPLETE_XPATH.match(xpath):
        xpath += '/text()'
    try:
        result = response.xpath(xpath).extract_first()
    except AttributeError:
        # Fall back to a more reliable (but more expensive) XPath parser.
        # This code was introduced in order to be able to parse:
        # http://files.luaforge.net/releases/luasocket/luasocket
        from lxml.html.soupparser import fromstring
        root = fromstring(response.body, features='lxml')
        try:
            result = root.xpath(xpath, namespaces={
                "re": "http://exslt.org/regular-expressions"})[0]
        except IndexError:
            result = None
    if result is None:
        return None
    return result.strip()


class XPath(Spider):
    name = 'xpath'
    params = {'base': '', 'date': '', 'date-url': None, 'no-date': False,
              'url-xpath': None, 'version': ''}

    def parse(self, response):
        version = _xpath(response, 'version')
        meta = response.meta
        if meta['url-xpath']:
            url = response.urljoin(_xpath(response, 'url-xpath'))
        else:
            url = response.url
        if meta['no-date']:
            date = None
        elif meta['date-url'] is not None:
            return Request(
                response.urljoin(_xpath(response, 'date-url')),
                callback=self.parse_date_from_header,
                meta={'response': response, 'url': url,
                      'version': version},
                method='HEAD',)
        elif meta['date'] or meta['base']:
            date = _xpath(response, 'date')
        else:
            date = None
        return Item(date=date, response=response, url=url, version=version)

    @staticmethod
    def parse_date_from_header(response):
        return Item(date=response.headers['Last-Modified'].decode('utf-8'),
                    **{k: response.meta[k]
                       for k in ('response', 'url', 'version')})

    def start_requests(self):
        return super().iter_start_requests(params=self.params)

    def first_request(self, data):
        return data['url']
