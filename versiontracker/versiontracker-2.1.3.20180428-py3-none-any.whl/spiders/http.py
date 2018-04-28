import re
from urllib.parse import urlparse

from scrapy import Request

from . import parse_date, PathSpider


IMG_PATTERN = "<img\s+(\S+\s+)*?src=\"[^\"]*\"\s*alt=\"[^\"]*\"(\s*/)?>"
A_START_PATERN = "<a\s+href=\"[^\"]*\"\s*>"
A_END_PATERN = "</a>"
PRE_LINE_RE = re.compile(
    r"^(?i)"
    r"(({img}|{a_start}{img}{a_end})\s*)?"
    r"<a\s+href=\"(?P<href>[^\"]*)\"\s*>[^<]*{a_end}\s*"
    r"(?P<date>\d{{2}}-\w{{3}}-\d{{4}} \d{{2}}:\d{{2}}|"
        r"\d{{4}}-\d{{2}}-\d{{2}}[T ]\d{{2}}:\d{{2}}(:\d{{2}}Z?)?)"
    r"\s*(?P<size>-|\d+(\.\d+)?k?\w?)".format(
        img=IMG_PATTERN, a_start=A_START_PATERN, a_end=A_END_PATERN))


class HTTP(PathSpider):
    name = 'http'

    def first_request(self, data):
        url = data['url']
        url_parts = urlparse(url)
        base_url = '{}://{}'.format(url_parts.scheme, url_parts.netloc)
        data['base_url'], data['path'] = base_url, url[len(base_url):]
        data['requires_index'] = False
        return super().first_request(data)

    def iter_entries(self, response):
        # Check for pre must go first because of scenarios where there is
        # an unrelated table before the pre element, such as in
        # http://goo.gl/ZjLGEd
        pre = response.xpath('//pre')
        # KDE’s starts with a pre that contains no tags, and the actual
        # content is on a table afterwards.
        if pre and pre.xpath('.//a'):
            for line in response.text.splitlines():
                match = PRE_LINE_RE.match(line.strip())
                if not match:
                    continue
                try:
                    date = parse_date(match.group('date'))
                except:
                    continue
                name = match.group('href').rstrip('/')
                yield {'name': name, 'date': date}
            return
        table = response.xpath('(//table)[{}]'.format(
            response.meta.get('table', 1)))
        if table:
            for tr in table.xpath('.//tr'):
                tds = tr.xpath('.//td')
                if not tds:
                    continue
                entry_column = 0
                while True:
                    img = tds[entry_column].xpath('.//img')
                    text = ' '.join(tds[entry_column].xpath(
                        './/text()').extract()).strip()
                    if not img and text:
                        break
                    entry_column += 1
                date_column = entry_column + 1
                date = None
                while True:
                    try:
                        date_string = tds[date_column].xpath(
                            './text()').extract_first().strip()
                        if not date_string or date_string == '\xa0':
                            break
                        date = parse_date(date_string)
                        break
                    except ValueError:
                        date_column += 1
                    except IndexError:
                        break
                if date is None:
                    continue
                name = tds[entry_column].xpath(
                    './/a/@href').extract_first().rstrip('/')
                if name[0] in '.?/':
                    continue
                yield {'name': name, 'date': date}
            return
        ul = response.xpath('//ul[@id=\'files\']')
        if ul:
            for li in ul.xpath('./li')[2:]:
                date = parse_date(
                    li.xpath('.//span[re:test(@class, \'\\bdate\\b\')]/'
                             'text()').extract_first())
                name = li.xpath('.//span[re:test(@class, \'\\bname\\b\')]'
                                '/text()').extract_first().strip().rstrip('/')
                yield {'name': name, 'date': date}
            return
        ul = response.xpath('//ul')
        if ul:
            for a in ul.xpath('./li/a')[1:]:
                name = a.xpath('./@href').extract_first().strip().rstrip('/')
                yield {'name': name}
            return
        raise NotImplementedError

    def parse_error(self, failure):
        meta = failure.request.meta
        meta['requires_index'] = True
        return Request(self.path_url(meta), meta=meta)

    def path_url(self, data):
        url = data['base_url'] + data['new_path']
        if data['requires_index']:
            url += 'index.html'
        return url
