"""Get version information of software products.

See :ref:`library-usage`.
"""

from collections import defaultdict
from os import environ, path
import re

from xdg.BaseDirectory import save_cache_path
import yaml

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from ._version import __version__ as version


_DATA = {}
_PATTERN_ALIASES = {
    'd mmm y': r'\d+\s+\w{3}\s+\d{4}',
    'n': r'\d+',
    'n.n': r'\d+(?:\.\d+)+',
    'n_n': r'(\d+)(?:_(\d+))?(?:_(\d+))?(?:_(\d+))?',
}


def _load_data():
    global _DATA
    if not _DATA:
        file_path = path.join(path.dirname(__file__), "data.yaml")
        with open(file_path, "r") as fp:
             data = yaml.load(fp)
        for key in list(data.keys()):
            if not isinstance(data[key], dict):
                if data[key] is None:
                    name = key
                else:
                    assert isinstance(data[key], str)
                    name = data[key]
                data[key] = {'spider': {'name': name}}
            elif 'spider' not in data[key]:
                data[key] = {'spider': data[key]}
            elif not isinstance(data[key]['spider'], dict):
                assert isinstance(data[key]['spider'], str)
                data[key]['spider'] = {'name': data[key]['spider']}
        _DATA = data
    return _DATA


class SoftwareEntryDefinitionError(RuntimeError):
    """Exception raised when a software entry in the :code:`data.yaml` file
    is not properly defined.

    The :code:`errors` property is a dictionary where keys are software IDs and
    values are dictionaries with the following format::

        {
            'invalid_keys': ('invalid_key_1', 'invalid_key_2', …)
        }
    """

    def __init__(self, errors, *args, **kwargs):
        self.errors = errors
        super().__init__(*args, **kwargs)


class UnknownSoftwareIDs(ValueError):
    """Exception raised when requesting version information for one or more
    unknown software IDs.

    The :code:`software_ids` property contains a sorted tuple of unknown
    received software IDs. The tuple never contains duplicate software IDs,
    even if those were received.
    """

    def __init__(self, software_ids, *args, **kwargs):
        self.software_ids = software_ids
        super().__init__(*args, **kwargs)


def _spiders(software_ids):
    software_entry_definition_errors = {}
    software_data = _load_data()
    spiders = defaultdict(list)
    unknown_software_ids = set()
    for software_id in software_ids:
        # Handle unknown software IDs.
        try:
            tracking_data = software_data[software_id]
        except KeyError:
            unknown_software_ids.add(software_id)
            continue
        if unknown_software_ids:
            # If an unknown software ID has been found already, we only need to
            # find out which other software IDs are unknown in order to provide
            # detailed error information.
            continue
        # Handle software entry definition errors.
        invalid_keys = tuple(key for key in sorted(tracking_data.keys())
                             if key not in ('spider', 'formatter'))
        if invalid_keys:
            software_entry_definition_errors[software_id] = {
                'invalid_keys': invalid_keys,
            }
            continue
        elif software_entry_definition_errors:
            # If a software entry with definition errors has been found
            # already, we only need to find out which other software entries
            # contain definition errors in order to provide detailed error
            # information.
            continue
        # Log spider target
        target = tracking_data['spider']
        target['id'] = software_id
        target['formatter'] = tracking_data.get('formatter', None)
        spiders[target['name']].append(target)
    if unknown_software_ids:
        raise UnknownSoftwareIDs(sorted(unknown_software_ids))
    if software_entry_definition_errors:
        raise SoftwareEntryDefinitionError(software_entry_definition_errors)
    return spiders


def compile_pattern(pattern):
    if pattern is None:
        return None
    return re.compile(
        _PATTERN_ALIASES[pattern] if pattern in _PATTERN_ALIASES else pattern)


class MissingSpiders(ValueError):
    """Exception raised when requesting version information for one or more
    software IDs the spiders of which do not exist.

    The :code:`data` property contains a dictionary where keys are software IDs
    and values are configured spider names that do not match any known spider.
    """

    def __init__(self, data, *args, **kwargs):
        self.data = data
        super().__init__(*args, **kwargs)


def iter_version_info(software_ids=()):
    """Given an iterable containing :meth:`supported software IDs
    <supported_software>`, it yields dictionaries with version information
    about them.

    The format of the yielded dictionary is the same as the format of the
    output dictionary of :meth:`version_info()`.

    .. note:: Yield order may not match input order.
    """
    # Parse spiders first to detect unknown software IDs early.
    spiders = _spiders(software_ids)
    settings = Settings({
        'BOT_NAME': 'versiontracker',
        'SPIDER_MODULES': ['versiontracker.spiders'],
        'NEWSPIDER_MODULE': 'versiontracker.spiders',
        'USER_AGENT': 'versiontracker/{} (+http://version-tracker.rtfd.io)'\
            .format(version),
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 64,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 64/2,
        'SPIDER_MIDDLEWARES': {
            'scrapy.spidermiddlewares.depth.DepthMiddleware': None,
            'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,
            'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': None,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
            'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None,
            'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
        },
        'EXTENSIONS': {
            'scrapy.extensions.corestats.CoreStats': None,
            'scrapy.extensions.logstats.LogStats': None,
            'scrapy.extensions.telnet.TelnetConsole': None,
        },
        'ITEM_PIPELINES': {
            'versiontracker.pipelines.Pipeline': 500,
        },
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 64/2/2,
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_DIR': save_cache_path('versiontracker'),
        'HTTPCACHE_POLICY': 'scrapy.extensions.httpcache.RFC2616Policy',
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'LOG_ENABLED': True,
        'LOG_LEVEL': 'WARNING',
        'STATS_CLASS': 'scrapy.statscollectors.DummyStatsCollector',
        'STATS_DUMP': False,
    })
    process = CrawlerProcess(settings)
    crawlers = []
    missing_spiders = {}
    for spider, targets in spiders.items():
        try:
            crawlers.append((process.create_crawler(spider), targets))
        except KeyError:
            for target in targets:
                missing_spiders[target['id']] = spider
    if missing_spiders:
        # If a missing spider was detected, we only need to check for
        # additional missing spiders of requested software entries.
        raise MissingSpiders(missing_spiders)
    for crawler, targets in crawlers:
        process.crawl(crawler, targets=targets)
    process.start()
    from .pipelines import result
    return result


def iter_software_ids_by_spider(spider):
    for software_id, tracking_data in _load_data().items():
        if spider == tracking_data.get('spider', {}).get('name', software_id):
            yield software_id


def supported_spiders():
    spiders = set()
    for software_id, tracking_data in _load_data().items():
        spiders.add(tracking_data.get('spider', {}).get('name', software_id))
    return tuple(spiders)


def supported_software():
    """Returns a list of supported software IDs that you can pass to
    :meth:`version_info()` or :meth:`iter_version_info()`."""
    return tuple(_load_data().keys())
