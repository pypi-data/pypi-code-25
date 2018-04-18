from __future__ import absolute_import

import os


# All Pyros Exception must be pickleable and have a message property
class PyrosException(Exception):

    """Basic exception for errors raised by Pyros"""
    def __init__(self, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "An exception was thrown in Pyros process %s" % os.getpid()
        super(PyrosException, self).__init__(msg)
        self.excmsg = msg

    @property
    def message(self):
        return self.excmsg

