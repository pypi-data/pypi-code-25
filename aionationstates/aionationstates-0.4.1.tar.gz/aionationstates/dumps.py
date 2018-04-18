import gzip
import urllib.request
from xml.etree import ElementTree as ET
from functools import partial

import aionationstates
from aionationstates.utils import actually_synchronous


class _ParsingFunctions:
    def __init__(self, interface_class):
        self._original_class = interface_class

    def __getattr__(self, name):
        return partial(
            actually_synchronous(getattr(self._original_class, name)._wrapped),
            None  # instead of self
        )


class DumpEntry:
    __slots__ = ()

    def __init__(self, elem):
        for name in self._attributes:
            setattr(self, name, getattr(self._parsing_functions, name)(elem))


class NationDumpEntry(DumpEntry):
    _parsing_functions = _ParsingFunctions(aionationstates.Nation)
    _attributes = __slots__ = [
        'name',
        'type',
        'fullname',
        'motto',
        'category',
        'wa',
        #'endorsements',
        'freedom',
        #'region',
        'population',
        'animal',
        'currency',
        'demonym',
        'demonym2',
        'demonym2plural',
        'flag',
        #'govt',
        #'freedomscores',
        #'deaths',
        'leader',
        'capital',
        'religion',
    ]


class RegionDumpEntry(DumpEntry):
    _parsing_functions = _ParsingFunctions(aionationstates.Nation)
    _attributes = __slots__ = [
    ]


def download_and_parse_dump(url, tag, cls):
    with urllib.request.urlopen(url) as fp:
        for _, elem in ET.iterparse(gzip.open(fp)):
            if elem.tag == tag:
                try:
                    yield cls(elem)
                except Exception:
                    print(elem.find('NAME').text)
                    raise
                elem.clear()
