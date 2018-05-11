#!/usr/bin/env python
# coding: utf-8

from unittest import TestCase
from .context import _StreamContext


class CatchStreamTestCase(TestCase):

    def catch_stream(slef, stream_type):
        """A function to return the context manager.

        Args:
            stream_type (str): The string of stream type: 'stdout' or 'stderr'

        Example:

            >>> with self.catch_stream("stdout") as stream:
            ...     print "Hello World!"

            >>> assert stream == "Hello World!"

        """

        context = _StreamContext(stream_type)
        return context
