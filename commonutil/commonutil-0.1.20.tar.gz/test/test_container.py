# -*- coding: utf-8 -*-
""" Testing for container module """

import unittest

from collections import OrderedDict
from itertools import izip

from commonutil import container


class Test_CountDownValuePopper(unittest.TestCase):
	def test_1(self):
		c = container.CountDownValuePopper(7, "*", (5, "x"), (3, "w"))
		exp_content = ("*", "*", "x", "x", "w", "w", "w")
		for idx, exp_v in enumerate(exp_content):
			t = c()
			self.assertEqual(exp_v, t, "index=%d <%r, %r>" % (idx, exp_v, t))


class Test_SealableOrderedDict(unittest.TestCase):
	def _validate(self, c, value_list):
		self.assertEqual(len(c), len(value_list), "length of resulted dictionary")
		for d0, d1, in izip(c.iteritems(), value_list):
			d0 = tuple(d0)
			d1 = tuple(d1)
			self.assertEqual(d0, d1)

	def test_seal_1(self):
		td_1 = [
				("d1", 1),
				("d2", 2),
				("d3", 3),
		]
		td_2 = [
				("d1", 1),
				("d2", 9),
				("d3", 3),
		]
		c = container.SealableOrderedDict()
		c["d1"] = 1
		c["d2"] = 2
		c.seal()
		c["d3"] = 3
		self._validate(c, td_1)
		with self.assertRaises(KeyError):
			c["d2"] = 9
		c.unseal()
		c["d2"] = 9
		self._validate(c, td_2)

	def test_update_1(self):
		td_1 = [
				("d1", 1),
				("d2", 2),
				("d3", 3),
				("d4", 4),
		]
		td_2 = [
				("d1", 1),
				("d2", 1),
				("d3", 3),
				("d4", 0),
				("d5", 5),
				("d6", 6),
		]
		td_3 = [
				("d1", 1),
				("d2", 1),
				("d3", 3),
				("d4", 0),
				("d5", 3),
				("d6", 6),
				("d7", 7),
		]
		c = container.SealableOrderedDict()
		c["d1"] = 1
		c["d2"] = 2
		c.update(OrderedDict([
				("d3", 3),
				("d4", 4),
		]))
		self._validate(c, td_1)
		c.update(OrderedDict([
				("d2", 1),
				("d4", 0),
				("d5", 5),
				("d6", 6),
		]))
		self._validate(c, td_2)
		c.seal()
		with self.assertRaises(KeyError):
			c.update(OrderedDict([
					("d5", 3),
					("d7", 7),
			]))
		self._validate(c, td_2)
		c.unseal()
		c.update(OrderedDict([
				("d5", 3),
				("d7", 7),
		]))
		self._validate(c, td_3)


if __name__ == '__main__':
	unittest.main()

# vim: ts=4 sw=4 ai nowrap
