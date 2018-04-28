from datetime import datetime

from scrapy.exceptions import DropItem

from . import compile_pattern
from .spiders import parse_date

# Global variable to keep result in memory.
result = []


def parse_item_date(item):
    value = item['date']
    if value is None or isinstance(value, datetime):
        return
    try:
        item['date'] = parse_date(value)
    except ValueError:
        raise DropItem(
            "Unknown format of date string '{}' of item '{}'.".format(
                item['date'], item['id']))


class Pipeline(object):

    def process_item(self, item, spider):
        # Load metadata
        response = item.pop('response')
        for k in ('date', 'id', 'url', 'version'):
            if k not in item and k in response.meta:
                item[k] = response.meta[k]
        if 'url' not in item:
            item['url'] = response.url
        formatter = response.meta['formatter']
        # Load formatting patterns
        if formatter is not None:
            if isinstance(formatter, str):
                patterns = {'version': formatter}
            else:
                patterns = {'version': formatter[0], 'date': formatter[1]}
            for field in list(patterns.keys()):
                patterns[field] = compile_pattern(patterns[field])
            # Format date
            date_re = patterns.get('date', None)
            if date_re is not None:
                if item['date'] is None:
                    raise DropItem("Date of item '{}' is None but it was "
                                   "expected to match pattern '{}'.".format(
                                        item['id'],date_re.pattern))
                match = date_re.search(item['date'])
                if not match:
                    raise DropItem("Pattern '{}' does not match date string "
                                   "'{}' of item '{}'.".format(
                                    date_re.pattern, item['date'], item['id']))
                groups, groupdict = match.groups(), match.groupdict()
                if groupdict:
                    item['date'] = "{y}-{m}-{d}".format(**groupdict)
                elif groups:
                    item['date'] = groups[0]
                else:
                    item['date'] = match.group(0)
            parse_item_date(item)
            # Format version
            version_re = patterns.get('version', None)
            if version_re.pattern == 'date':
                if item['date'] is None:
                    raise DropItem("Date of item '{}' is None and version "
                                   "pattern is 'date'.".format(item['id']))
                else:
                    item['version'] = item['date'].strftime("%Y%m%d")
            else:
                match = version_re.search(item['version'])
                if not match:
                    raise DropItem(
                        "Pattern '{}' does not match version string '{}' of "
                        "item '{}'.".format(
                            version_re.pattern, item['version'], item['id']))
                groups = match.groups()
                if groups:
                    item['version'] = ".".join(tuple(group for group in groups
                                                     if group is not None))
                else:
                    item['version'] = match.group(0)
        else:
            parse_item_date(item)
        global result
        result.append(dict(item))
        return item
