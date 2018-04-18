# -*- coding: utf-8 -*-

""" pourover.functions

This module contains parsing functions provided by pourover

:copyright: (c) Zachary Hart
:license: Apache 2.0, see LICENSE for more details.
"""

import re

from collections import OrderedDict
from datetime import datetime

from .exceptions import CEFMessageError, IncompleteMessageError
from .models import CEFMessage, CEFLog


# regular expressions needed for parsing, kept out of the functions for ease of reading
HEADER_SEP = r'(.*(?<!\\)\|){,7}(.*)'
HEADER_SPLIT = r'(?<!\\)\|'
SYSLOG_SEP = r'[a-zA-Z]{3}\s+[0-9]{,2}\s(?:[[0-9]{2}:*){3}\s+\w+'
EXTENSION_MATCH = r'([^=\s]+)=((?:[\\]=|[^=])+)(?:\s|$)'


def parse_line(line):
    """ Parse a CEF formatted log line

    Parse the data and fields from a log line in CEF format and return them in an easy-to-manipulate dict, breaking
    extensions into the key-value pairs presented in the log line.

    :param line: A CEF formatted line, beginning with a CEF header and ending in any present extensions
    :type line: str
    :return: The parsed line object
    :rtype: :class:`CEFMessage <CEFMessage>`
    """
    if not isinstance(line, str):
        raise TypeError('CEF Lines must be strings')

    # Create groups within the CEF line of the header (including a syslog prefix, if present)
    split_at_header = re.search(HEADER_SEP, line)
    if not split_at_header:
        # If we can't match anything
        raise CEFMessageError('A valid CEF header could not be found!')

    header = split_at_header.group(1)
    extensions = split_at_header.group(2)

    if header is None:
        # If a valid header couldn't be found
        raise CEFMessageError('A valid CEF header could not be found!')

    # Create some empty dicts for later
    header_dict = OrderedDict()
    extension_dict = OrderedDict()

    # Now we want to split up our header - making sure not to split on escaped pipe characters on accident
    header_values = re.split(HEADER_SPLIT, header)

    # First we need to determine if there's a syslog prefix
    split_at_syslog_prefix = re.search(SYSLOG_SEP, header_values[0])
    if split_at_syslog_prefix:
        header_dict['Prefix'] = split_at_syslog_prefix.group(0)

    # Add all headers into our dict
    header_dict['Version'] = header_values[0].split(' ')[-1].split(':')[1]
    header_dict['DeviceVendor'] = header_values[1]
    header_dict['DeviceProduct'] = header_values[2]
    header_dict['DeviceVersion'] = header_values[3]
    header_dict['DeviceEventClassID'] = header_values[4]
    header_dict['Name'] = header_values[5]
    header_dict['Severity'] = header_values[6]

    # Split up our extensions and insert them into their own dict
    extension_pairs = re.findall(EXTENSION_MATCH, extensions)
    for pair in extension_pairs:
        extension_dict[pair[0]] = pair[1]

    # Create a CEFMessage object and populate it
    cefline = CEFMessage()

    cefline.extensions = extension_dict
    cefline.headers = header_dict

    cefline.__setattr__('_extension_count', len(extension_dict))
    cefline.__setattr__('_raw_line', line)
    cefline.__setattr__('_raw_header', header)

    return cefline


def parse_file(filepath):
    """ Parse all messages in a CEF formatted log file

    Parse the data and fields from a file in CEF format and return them in a easy-to-manipulate list, breaking
    extensions into the key-value pairs presented in the log line

    :param filepath: The file to parse log lines from
    :type filepath: str
    :return: The parsed log object
    :rtype: :class:`CEFLog <CEFLog>`
    """
    log = CEFLog()
    with open(filepath, 'r') as logfile:
        messages = logfile.readlines()
        for logline in messages:
            line = parse_line(logline)
            log.append(line)

    return log


def create_line(version, dev_vendor, dev_product, dev_version, dev_event_class_id, name, severity, set_syslog_prefix=False, timestamp=None, hostname=None, **kwargs):
    """ Return a CEF formatted log line from header values and any extensions

    Format CEF header values plus any provided key-value pairs of extensions into a CEF formatted log line

    :param version: CEF version number
    :param dev_vendor: Device Vendor
    :param dev_product: Device Product
    :param dev_version: Device Version
    :param dev_event_class_id: Device Event Class ID
    :param name: Name
    :param severity: Severity
    :param set_syslog_prefix: Optionally include the syslog timestamp and host
    :param timestamp: If including a syslog prefix, the time to include in the prefix. If this value is not provided,
        the log entry will have the datetime at which this function was called
    :param hostname: If including a syslog prefix, the hostname to include in the prefix
    :param kwargs: key-value pairs of extensions
    :type version: int
    :type dev_vendor: str
    :type dev_product: str
    :type dev_version: str
    :type dev_event_class_id: int
    :type name: str
    :type severity: int
    :type set_syslog_prefix: bool
    :type timestamp: datetime
    :type hostname: str
    :return: A created line object
    :rtype: :class:`CEFMessage <CEFMessage>`
    """
    # TODO: Escape special characters in parameters
    # Join our parameters into the header with a pipe character
    header = 'CEF:' + '|'.join(
            [str(version), dev_vendor, dev_product, dev_version, str(dev_event_class_id), name, str(severity)]
    ) + '|'

    if set_syslog_prefix:
        if not hostname:
            # We need a hostname to create a syslog prefix
            raise IncompleteMessageError('No hostname was provided for the requests syslog prefix')
        if timestamp:
            syslog_prefix = timestamp.strftime('%b %d %H:%M:%S')
        else:
            syslog_prefix = datetime.utcnow().strftime('%b %d %H:%M:%S')

        # add the hostname to the prefix
        syslog_prefix = syslog_prefix + ' ' + hostname

        # add the prefix to the header
        header = syslog_prefix + ' ' + header

    # add any kwargs passed as extensions
    for k, v in kwargs.items():
        header += '%s=%s ' % (k, v)

    # remove the trailing space
    header = header[:-1]

    cefline = parse_line(header)
    return cefline
