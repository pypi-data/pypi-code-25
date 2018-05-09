from __future__ import absolute_import

import pynbody

class IsolatingSubSnapWrapper(pynbody.snapshot.SimSnap):
    """This class implements a SubSnap object which prevents access to its base.

    It is used to ensure consistent behaviour between analyses whether or not a full simulations snapshot is loaded
    See issue #42.
    """
    def __init__(self, subsnap):
        self._underlying = subsnap

    def __getattribute__(self, name):
        if name=='base' or name=='ancestor':
            return self
        return getattr(object.__getattribute__(self, "_underlying"), name)

    def __setattr__(self, key, value):
        setattr(object.__getattribute__(self, "_underlying"), key, value)

    def __delattr__(self, key):
        delattr(object.__getattribute__(self, "_underlying"), key)