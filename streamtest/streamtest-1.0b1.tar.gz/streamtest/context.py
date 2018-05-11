#!/usr/bin/env python
# coding: utf-8

import sys
from cStringIO import StringIO


class _StreamContext(object):
    """A context manager used to implement catch_stream methods."""

    def __init__(self, stream_type="stdout"):

        self.fake_stream = StringIO()
        self.stream_type = stream_type

        self.flag_of_catched = False

    def catch(self):
        """Change the standard stream for getting a stream output."""

        if self.stream_type == "stdout":
            sys.stdout = self.fake_stream

        elif self.stream_type == "stderr":
            sys.stderr = self.fake_stream

    def release(self):
        """Restore the fake stream to genuine."""

        if self.stream_type == "stdout":
            sys.stdout = sys.__stdout__

        elif self.stream_type == "stderr":
            sys.stderr = sys.__stderr__

        self.flag_of_catched = True

    @property
    def output(self):
        """Get the stream output from fake stream."""

        if self.flag_of_catched:
            return self.fake_stream.getvalue()

        else:
            return None

    def __enter__(self):

        self.catch()
        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self.release()

    def __eq__(self, other):

        if isinstance(other, _StreamContext):
            return (self.output == other.output)

        else:
            return (self.output == other)

    def __ne__(self, other):

        return not self.__eq__(other)

    def __repr__(self):

        return self.output

    def __str__(self):

        return self.output
