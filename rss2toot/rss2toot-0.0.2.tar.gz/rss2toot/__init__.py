# -*- coding: utf-8 -*-
"""
rss2toot
~~~~~~~~~~~~~~~~~~~~~

rss2toot is library written in Python which emits mastodon toot messages
from given rss feed.

usage:

   >>> import rss2toot

:copyright: (c) 2018 by Peter Zahradnik.
:license: BSD-2-Clause, see LICENSE for more details.
"""
import logging
from logging import NullHandler
from .rss2toot import Rss2Toot, Rss2TootItem, Rss2TootCache, toot

logging.getLogger(__name__).addHandler(NullHandler())
