from copy import deepcopy
from datetime import datetime
import re

import dateutil.parser

from scrapy import Request, Spider as _BaseSpider

from ..items import Item


_DATE_TRASH_RE = re.compile("(--|[][()])")


def git_service_url(template, target, commit_suffix, tag_suffix):
    """Given an URL template that may contain placeholders for :code:`project`
    and :code:`repository`, a dictionary of parameters for a given software
    product, a URL suffix for commit searches and a URL suffix for tag
    searches, it returns the corresponding URL."""
    url = target.get('url', None)
    if url is None:
        url = template.format(**{k: target.get(k, target['id'])
                                 for k in ('project', 'repository')})
    return url + (commit_suffix if target.get('commit', None) else tag_suffix)


# Note: The purpose of removing trash from the date string is to be
# able to handle dates such as ‘Mon, 6 Jun 2016 -- 11:00 (-0400)’,
# which you can see at
# http://download.eclipse.org/eclipse/downloads/
# or ‘2016-11-25T02:36:45 [GMT]’, which you can see at
# http://www.jedsoft.org/releases/slang/
def parse_date(date_string):
    """Returns a :code:`datetime` object created based on the specified date
    string."""
    if date_string is None or isinstance(date_string, datetime):
        return date_string
    return dateutil.parser.parse(_DATE_TRASH_RE.sub("", date_string))


class Spider(_BaseSpider):
    """Base class for Version Tracker spiders that fetch version information
    for one or more software products."""

    def __init__(self, targets, *args, **kwargs):
        self.targets = targets
        super(Spider, self).__init__(*args, **kwargs)

    def iter_start_requests(self, params=None):
        if params is None:
            params = {}
        params['formatter'] = params.get('formatter', None)
        for target in self.targets:
            meta = deepcopy(params)
            meta.update(target)
            request = self.first_request(meta)
            if isinstance(request, Request):
                yield request
            else:
                yield Request(request, meta=meta)

    def parse(self, response):
        raise NotImplementedError

    def start_requests(self):
        return self.iter_start_requests()

    def first_request(self, data):
        raise NotImplementedError


def value_from_match(match, fallback=None):
    """Returns the first capture group of `match`, the whole match if there are
    no capture groups, or `fallback` if `match` is `None`.

    See :ref:`creating-path-spiders` for an example usage.
    """
    try:
        return match.group(1)
    except IndexError:
        return match.group(0)
    except AttributeError:
        return fallback


class GitSpider(Spider):
    """Base class for :ref:`Git spiders <git-spiders>`."""

    def item(self, response, string):
        pattern = response.meta.get('commit', None) or response.meta['tag']
        match = re.search(pattern, string)
        if match:
            return Item(response=response, version=value_from_match(match))
        return None

    @staticmethod
    def searching_commits(response):
        return bool(response.meta['commit'])

    def start_requests(self):
        return self.iter_start_requests(
            params={'commit': None, 'tag': None})

    def first_request(self, data):
        if not any(data[k] is not None for k in ('commit', 'tag')):
            data['tag'] = '(?i)^(?:v|(?:{}|release|stable)-)?(.*)$'.format(
                re.escape(data['id']))


_NUMBER_RE = re.compile('\\d+')


def _highest_key_function(item):
    return tuple(int(i) for i in _NUMBER_RE.findall(item['name']))


class PathSpider(Spider):
    """Base class for :ref:`Path spiders <path-spiders>`."""

    BREADCRUMBS = {
        "highest": _highest_key_function,
        "latest": lambda k: parse_date(k['date']),
    }
    DEFAULT_PATH = r'${latest:(\d+\.\d+(\.\d+(\.\d+)?)?)}'

    def _next_path(self, data):
        match_failures = data['match_failures']
        start = data['start']
        for i, breadcrumb in enumerate(data['breadcrumbs'][start:],
                                       start=start):
            data['start'] = i
            for keyword, key_function in self.BREADCRUMBS.items():
                if breadcrumb.startswith("${" + keyword):
                    data['resolvable_index'] += 1
                    data['skip'] = 0
                    if (match_failures and data['resolvable_index'] ==
                            data['resolvable_count'] - 1):
                        data['skip'] = match_failures
                    data['breadcrumb'] = breadcrumb
                    data['keyword'] = keyword
                    data['key_function'] = key_function
                    return Request(
                        self.path_url(data), meta=data, callback=self.parse,
                        errback=self.parse_error)
            else:
                assert i != data['last_breadcrumb_index']
                data['new_path'] += breadcrumb + '/'
        assert False

    def first_request(self, data):
        path = data['path']
        if not path.endswith("}"):
            path = path.rstrip('/') + '/' + self.DEFAULT_PATH
        breadcrumbs = path.strip('/').split('/')
        resolvable_count = path.count("${latest") + path.count("${highest")
        data.update({
            'breadcrumbs': breadcrumbs,
            'last_breadcrumb_index': len(breadcrumbs)-1,
            'match_failures': 0,
            'new_path': '/',
            'resolvable_count': resolvable_count,
            'resolvable_index': 0,
            'start': 0,
        })
        data['original_data'] = deepcopy(data)
        return self._next_path(data)

    def iter_entries(self, response):
        raise NotImplementedError

    def parse(self, response):
        meta = response.meta
        breadcrumb, keyword, key_function, skip = (
            meta.pop(k)
            for k in ('breadcrumb', 'keyword', 'key_function', 'skip'))
        entries = [entry for entry in self.iter_entries(response)]
        entry_re = None
        if ':' in breadcrumb:
            entry_re = re.compile(breadcrumb[len(keyword) + 3:-1])
        for entry in sorted(entries, key=key_function, reverse=True):
            match = None
            if entry_re:
                match = entry_re.search(entry["name"])
                if not match:
                    continue
            if skip > 0:
                skip -= 1
                continue
            if meta['start'] == meta['last_breadcrumb_index']:
                version = value_from_match(match, entry["name"])
                if 'date' not in entry:
                    return Request(
                        response.urljoin(entry["name"]),
                        callback=self.parse_date_from_header,
                        meta={'response': response, 'url': response.url,
                              'version': version},
                        method='HEAD',)
                return Item(date=entry['date'], response=response,
                            url=response.url, version=version)
            else:
                meta['start'] += 1
                meta['new_path'] += entry['name'] + '/'
                return self._next_path(meta)
        match_failures = meta['match_failures']
        if match_failures > 3:
            # A single match failure should be enough. Anything more
            # may be an endless loop.
            raise NotImplementedError(
                'Review the configuration of {}, the specified breadcrumbs '
                'seem to lead to an endless loop.'.format(response.meta['id']))
        meta = meta['original_data']
        meta['original_data'] = deepcopy(meta)
        meta['match_failures'] = match_failures + 1
        return self._next_path(meta)

    @staticmethod
    def parse_date_from_header(response):
        return Item(date=response.headers['Last-Modified'].decode('utf-8'),
                    **{k: response.meta[k]
                       for k in ('response', 'url', 'version')})

    def parse_error(self, failure):
        pass

    def path_url(self, data):
        raise NotImplementedError

    def start_requests(self):
        return super().iter_start_requests(params={'path': self.DEFAULT_PATH})
