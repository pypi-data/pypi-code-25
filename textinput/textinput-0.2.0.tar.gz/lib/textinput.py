#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division

"""
textinput: streamlined version of stdlib fileinput

Typical use is:

    import textinput
    for line in textinput.lines():
        process(line)

This iterates over the lines of all files listed in sys.argv[1:],
defaulting to sys.stdin if the list is empty.  If a filename is '-' it
is also replaced by sys.stdin.  To specify an alternative list of
filenames, pass it as the argument to input().  A single file name is
also allowed.

Many auxiliary functions of fileinput are not supported. They are both
awkward and incur a performance penalty. The philosophy of textinput
is that a programmer who needs lineno() should be using enumerate() on
lines() instead.

Global state is not supported.

"files" changed to "filenames"
"""

__version__ = "$Revision: 1.7 $"

# Copyright 2005-2007 Michael M. Hoffman <hoffman+software@ebi.ac.uk>

# XXX: add support for URLs
# XXX: add command-line mode that evaluates a Python string

import sys

def _get_filenames(filenames):
    if filenames is None:
        filenames = sys.argv[1:]
    if not filenames:
        filenames = ['-']

    return filenames

def files(filenames=None, **kwargs):
    """usage:

    for textfilename, textfile in files(filenames):
        pass
    """
    for filename in _get_filenames(filenames):
        yield filename, open(filename, **kwargs)

def lines(filenames=None, **kwargs):
    # XXX: consider closing the file using with_statement
    # use an option to say if we don't want the file closed

    for filename in _get_filenames(filenames):
        for line in open(filename, **kwargs):
            yield line

def open(filename, *args, **kwargs):
    """Works like built-in file() but returns sys.stdin for -"""
    # XXX: arrange for modes w and b for -:
    # filename == "-", mode == "w" => sys.stdout
    # mode == "b" => see this web page:
    # http://groups-beta.google.com/group/comp.lang.python/browse_frm/thread/e903180cabc62ee7/b7310b2ede2acaea

    if filename == "-":
        if args:
            raise ValueError("can't specify args with filename '-'")
        if kwargs:
            raise ValueError("can't specify kwargs with filename '-'")
        return sys.stdin

    return open(filename, *args, **kwargs)

def main(args):
    pass

def _test(*args, **kwargs):
    import doctest
    doctest.testmod(sys.modules[__name__], *args, **kwargs)

if __name__ == "__main__":
    if __debug__:
        _test()
    sys.exit(main(sys.argv[1:]))