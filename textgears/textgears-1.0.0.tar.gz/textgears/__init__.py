#!/usr/bin/env python
# coding: utf-8

import requests

__author__ = "Hayato Tominaga"
__author_email__ = "takemehighermore@gmaill.com"
__license__ = "MIT License"
__version__ = "1.0.0"


class CheckResult(object):
    """A simple object for storing data of checked grammar."""

    def __init__(self, data):
        """Initialize of class.

        Args:
            data: The instance of `requests.Response`."""

        self.raw = data
        self.index = data.get("index", 0)
        self.result = data.get("result")

    @property
    def errors(self):
        """Make the error data of checked grammar to the dictionary object.

        Returns:
            The dictionary object: {errors["bad"]: errors["better"]}"""

        errors_raw = self.raw.get("errors")
        error_map_tuple = map(
            (lambda e: (e.get("bad"), e.get("better"))), errors_raw
        )

        return dict(error_map_tuple)

    def __eq__(self, other):

        return len(self.errors) == len(other.errors)

    def __ne__(self, other):

        return not self.__eq__(other)

    def __iter__(self):

        return self

    def next(self):

        if self.index >= len(self.errors):
            self.index = 0
            raise StopIteration

        key = self.errors.keys()[self.index]
        self.index += 1
        return {key: self.errors[key]}

    def __repr__(self):

        return repr(self.errors)


class TextGears:
    """A class of `textgears.com` API client."""

    def __init__(self, apikey):
        """Initialize of class.

        Args:
            apikey (str): the API key of `textgears.com`.
        """

        self.key = apikey
        self.url = "https://api.textgears.com/check.php"

    def check(self, text):
        """Check the grammar of English.

        Args:
            text (str): an English text.

        Returns:
            The instance of CheckResult object what contains checked result
            data."""
        response = self.access(text)
        data = response.json()

        return CheckResult(data)

    def access(self, text):
        """Access to the `textgears.com` API.

        Returns:
            the instance of `requests.Response` class."""

        params = {"text": text, "key": self.key}
        return requests.post(self.url, params=params)


def check(text, apikey):
    """Check the grammar of English by `textgears.com` API.

    >>> import textgears
    >>> result = textgears.check("I is an engeneer!", apikey="YOUR API KEY")
    >>> result.errors
    {u'is': [u'am'], u'engeneer': [u'engineer', u'engender']}
    >>> for error in result:
    ...     print error
    {u'is': [u'am']}
    {u'engeneer': [u'engineer', u'engender']}

    Args:
        text (str): an English text.
        apikey (str): the API key of `textgears.com`.

    Returns:
        The instance of `CheckResult` object what contains checked result data.
    """

    client = TextGears(apikey=apikey)
    return client.check(text)
