from datetime import datetime, timedelta
import re

from ..items import Item

from . import parse_date, Spider


_RELATIVE_TIME_RE = re.compile(
    r"^(?P<hours>\d+) hours? ago|(?P<days>\d+) days? ago$")


def timedelta_from_string(string):
    match = _RELATIVE_TIME_RE.match(string)
    kwargs = {k: -int(v) for k, v in match.groupdict().items()
              if v is not None}
    return timedelta(**kwargs)


class OpenDesktop(Spider):
    name = 'opendesktop'

    @staticmethod
    def extract(response, field_name):
        return response.xpath(
            '//div[re:test(@class, \'\\bdetails\\b\')]'
            '//div[re:test(@class, \'\\brow\\b\')]'
            '[re:test(span/text(), \'\\b{}\\b\')]'
            '//span[re:test(@class, \'\\bvalue\\b\')]/text()'
            ''.format(field_name)).extract_first().strip()

    def parse(self, response):
        date = (self.extract(response, 'updated') or
                self.extract(response, 'added'))
        try:
            date = parse_date(date)
        except ValueError:
            date = datetime.now() + timedelta_from_string(date)
        version = self.extract(response, 'version')
        return Item(date=date, response=response, version=version)

    def first_request(self, data):
        site = data.get('site', 'linux-apps')
        suffix = 'com' if site == 'linux-apps' else 'org'
        if '.' not in site:
            site = 'www.' + site
        return 'https://{}.{}/p/{}/'.format(site, suffix, data['project'])
