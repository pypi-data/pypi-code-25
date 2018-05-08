# Copyright (C) 2010, 2011, 2017 Canonical Ltd.
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

"""OOPS config and publishing for Twisted.

This module acts as an adapter for the oops.Config module - see `pydoc
oops.Config` for the primary documentation.

The only change is that Config.publish works with deferreds.

A helper function defer_publisher is supplied which can wrap a non-deferred
publisher.
"""

from __future__ import absolute_import, print_function

from functools import partial
import warnings

import oops
from twisted.internet import defer
from twisted.internet.threads import deferToThread

from oops_twisted.createhooks import failure_to_context
from oops_twisted.publishers import (
    convert_result_to_list,
    publish_to_many,
    )

__all__ = [
    'Config',
    'defer_publisher',
    ]


class Config(oops.Config):
    """Twisted version of oops.Config.

    The only difference is that the publish method, which could block now
    expects each publisher to return a deferred.

    For more information see the oops.Config documentation.
    """

    def __init__(self, *args, **kwargs):
        oops.Config.__init__(self)
        self.on_create.insert(0, failure_to_context)

    @defer.inlineCallbacks
    def publish(self, report):
        """Publish a report.

        The report is first synchronously run past self.filters, then fired
        asynchronously at self.publisher.

        See `pydoc oops.Config.publish` for more documentation.

        :return: a twisted.internet.defer.Deferred. On success this deferred
            will return the list of oops ids allocated by the publishers (a
            direct translation of the oops.Config.publish result).
        """
        for report_filter in self.filters:
            if report_filter(report):
                defer.returnValue(None)
        # XXX cjwatson 2017-09-02 bug=1015293: Remove this once users have
        # had a chance to migrate.
        if self.publishers:
            warnings.warn(
                "Using the oops_twisted.Config.publishers attribute is "
                "deprecated. Use the oops_twisted.Config.publisher attribute "
                "instead, with an oops_twisted.publishers.publish_to_many "
                "object if multiple publishers are needed",
                DeprecationWarning, stacklevel=2)
        old_publishers = [convert_result_to_list(p) for p in self.publishers]
        if self.publisher:
            publisher = publish_to_many(self.publisher, *old_publishers)
        else:
            publisher = publish_to_many(*old_publishers)
        ret = yield publisher(report)
        if ret:
            report['id'] = ret[-1]
        defer.returnValue(ret)


def defer_publisher(publisher):
    """Wrap publisher in deferToThread."""
    return partial(deferToThread, publisher)
