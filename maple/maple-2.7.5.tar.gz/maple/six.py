# -*- coding: utf-8 -*-

import sys


# Useful for very coarse version differentiation.
PY3 = sys.version_info[0] == 3


if PY3:
    import _thread
else:
    import thread as _thread
