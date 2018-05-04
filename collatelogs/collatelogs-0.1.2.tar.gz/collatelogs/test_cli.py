import unittest

from . import cli


class TestCli(unittest.TestCase):
    cli.main(['foo'])
