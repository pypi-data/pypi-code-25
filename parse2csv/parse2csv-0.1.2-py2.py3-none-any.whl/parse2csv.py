# coding=utf-8

"""
    parse2csv.parse2csv
    ~~~~~~~~~~~~~~~~~~~

    The main module.

    :copyright: (c) 2018 by Ali Ghaffaari.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import division
from collections import defaultdict
import csv

import yaml
import parse


class Reduce(object):
    """Supported reduce functions."""
    @staticmethod
    def first(values):
        """Get the first value."""
        return values[0]

    @staticmethod
    def last(values):
        """Get the last value."""
        return values[-1]

    @staticmethod
    def avg(values):
        """Get average of the values."""
        return sum(values) / len(values)

    @staticmethod
    def avg_tp(values):
        """Get average of the values by preserving its original type."""
        return type(values[0])(sum(values) / len(values))

    @staticmethod
    def count(values):
        """Get the number of values."""
        return len(values)

    @staticmethod
    def min(values):
        """Get the minimum value."""
        return min(values)

    @staticmethod
    def max(values):
        """Get the maximum value."""
        return max(values)

    @staticmethod
    def sum(values):
        """Get the sum of values."""
        return sum(values)

    @staticmethod
    def concat(values):
        """Get concatenation of the values."""
        return ''.join(values)


def process(data, funcs):
    """Process multi-value fields by applying specified reduce function.

    Args:
        data : dict
            The data to be processed.
        funcs : dict
            A dictionary specifying the reduce function for each multi-value
            field. In case that it is not specified for a particular field it
            is assumed to be `Reduce.first` function.
    """
    reducts = defaultdict(lambda: 'first')
    reducts.update(funcs)
    proc_data = dict()
    for key, values in data.items():
        func = getattr(Reduce, reducts[key])
        proc_data[key] = func(values)
    return proc_data


def parse_all(content, patterns):
    """Extract the fields from the content.

    Args:
        content : str
            The content to be parsed.
        patterns : list of str
            The list of patterns to find.
    """
    data = defaultdict(list)
    for pat in patterns:
        for match in parse.findall(pat, content):
            for key, value in match.named.items():
                data[key].append(value)
    return data


def list_dialects():
    """Get list of supported CSV dialects."""
    return csv.list_dialects()


def default_dialect():
    """Get default CSV dialects."""
    return 'unix'


def generate(output, inputs, configfile, dialect='unix'):
    """Generate CSV file.

    Args:
        output : file-like object
            Output file.
        inputs : list of file-like objects
            Input files to be processed.
        configfile : file-like object
            Input configuration file.
        dialect : str
            This string specifies the dialect of the output CSV file.
    """
    config = yaml.load(configfile)
    writer = csv.DictWriter(output,
                            fieldnames=config['fields'],
                            restval=config.get('missing_value', 'NA'),
                            extrasaction='ignore',
                            dialect=dialect,
                            quoting=csv.QUOTE_NONE)
    writer.writeheader()
    for inp in inputs:
        data = parse_all(inp.read(), config['patterns'])
        proc_data = process(data, config.get('reduce', {}))
        writer.writerow(proc_data)
