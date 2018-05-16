# -*- coding: utf-8 -*-
""" Testing for convert module """

import unittest

from collections import OrderedDict

from commonutil import convert


class Test_ToText(unittest.TestCase):
	def test_normal_string_1(self):
		r = convert.to_text("normal string")
		self.assertEqual(r, "normal string")

	def test_normal_string_2(self):
		r = convert.to_text("   normal string")
		self.assertEqual(r, "normal string")

	def test_normal_string_3(self):
		r = convert.to_text("normal string   ")
		self.assertEqual(r, "normal string")

	def test_empty_string_1(self):
		r = convert.to_text("")
		self.assertIsNone(r)

	def test_empty_string_2(self):
		r = convert.to_text(None)
		self.assertIsNone(r)

	def test_empty_string_3(self):
		r = convert.to_text(None, "-")
		self.assertEqual(r, "-")


class Test_ToList(unittest.TestCase):
	def test_string_1(self):
		r = convert.to_list("abc", convert.to_text)
		self.assertEqual(r, [
				"abc",
		])

	def test_iterator_1(self):
		d = OrderedDict()
		d["c1"] = 1
		d["a2"] = 2
		d["b3"] = 3
		r = convert.to_list(d.iteritems(), tuple)
		self.assertEqual(r, [
				("c1", 1),
				("a2", 2),
				("b3", 3),
		])


if __name__ == '__main__':
	unittest.main()

# vim: ts=4 sw=4 ai nowrap
