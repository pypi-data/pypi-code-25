# Copyright (C) 2017 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

"""Asynchronous publisher utilities."""

from __future__ import absolute_import, print_function

__all__ = [
    'convert_result_to_list',
    'publish_to_many',
    'publish_with_fallback',
    ]

from twisted.internet import defer


def publish_with_fallback(*publishers):
    """An asynchronous fallback publisher of oops reports.

    This is a publisher; see Config.publish for the calling and return
    conventions. This publisher delegates to the supplied publishers
    by calling them all until one reports that it has published the
    report, and aggregates the results.

    This is a version of `oops.publishers.publish_with_fallback` suitable
    for use with Twisted.

    :param *publishers: a list of callables to publish oopses to.
    :return: a callable that will return a Deferred; on success this will
        have published a report to each of the publishers.
    """
    @defer.inlineCallbacks
    def publish(report):
        ret = []
        for publisher in publishers:
            published = yield publisher(report)
            ret.extend(published)
            if ret:
                break
        defer.returnValue(ret)
    return publish


def publish_to_many(*publishers):
    """An asynchronous fan-out publisher of oops reports.

    This is a publisher; see Config.publish for the calling and return
    conventions. This publisher delegates to the supplied publishers
    by calling them all, and aggregates the results.

    If a publisher returns a non-emtpy list (indicating that the report was
    published) then the last item of this list will be set as the 'id' key
    in the report before the report is passed to the next publisher. This
    makes it possible for publishers later in the chain to re-use the id.

    This is a version of `oops.publishers.publish_to_many` suitable for use
    with Twisted.

    :param *publishers: a list of callables to publish oopses to.
    :return: a callable that will return a Deferred; on success this will
        have published a report to each of the publishers.
    """
    @defer.inlineCallbacks
    def publish(report):
        ret = []
        for publisher in publishers:
            if ret:
                report['id'] = ret[-1]
            published = yield publisher(report)
            ret.extend(published)
        defer.returnValue(ret)
    return publish


def convert_result_to_list(publisher):
    """Ensure that an asynchronous publisher returns a list.

    The old protocol for publisher callables was to return an id, or
    a False value if the report was not published. The new protocol
    is to return a list, which is empty if the report was not
    published.

    This function converts a publisher using the old protocol into one that
    uses the new protocol, translating values as needed.
    """
    @defer.inlineCallbacks
    def publish(report):
        ret = yield publisher(report)
        if ret:
            defer.returnValue([ret])
        else:
            defer.returnValue([])
    return publish
