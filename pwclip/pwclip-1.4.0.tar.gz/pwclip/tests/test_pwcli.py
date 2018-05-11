"""
import sys
from unittest import TestCase
from pwclip.cmdline import argspars, confargs, cli

class CommandLineTestCase(TestCase):
	@classmethod
	def setUpClass(cls):
		cls.parser = argspars('cli')
		cls.args, cls.pargs, cls.pkwargs = cls.parser


class TestCase4pwcli(CommandLineTestCase):
	def test_with_empty_args():
		with self.assertRaises(SystemExit):
			self.parser.parse_args([])

	def test_list_entrys():
		cli(confsargs())
"""
