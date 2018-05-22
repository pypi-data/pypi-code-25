# -*- coding: utf-8 -*-
"""Browser utilities."""

from ps.plone.mls import utils
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.browser import BrowserView


class IUtilities(Interface):
    """Some common utilities for the MLS Embedding."""

    def smart_truncate(content):
        """Truncate a string for some max length but split at word boundary."""


@implementer(IUtilities)
class Utilities(BrowserView):
    """Some common utilities for the MLS Embedding."""

    def smart_truncate(self, content):
        return utils.smart_truncate(content)
