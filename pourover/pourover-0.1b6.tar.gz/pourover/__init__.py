#  _____
# |  __ \
# | |__) |__  _   _ _ __ _____   _____ _ __
# |  ___/ _ \| | | | '__/ _ \ \ / / _ \ '__|
# | |  | (_) | |_| | | | (_) \ V /  __/ |
# |_|   \___/ \__,_|_|  \___/ \_/ \___|_|

""" Pourover CEF Parsing Library

Pourover is a CEF Parsing Library, written in python, for lizard people.

GitHub is the ultimate social media and this is just a subtweet

:copyright: (c) 2018 by Zachary Hart
:license: Apache 2.0, see LICENSE for more details
"""

from .__version__ import __title__, __description__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__

from .functions import parse_line, parse_file, create_line
from .models import CEFLog, CEFMessage
from .exceptions import (
    PouroverException, CEFMessageError, IncompleteMessageError, UnsupportedValueError, CEFLogError, SyslogPrefixError
)

import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
