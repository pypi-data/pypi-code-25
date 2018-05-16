# -*- coding: utf-8 -*-
""" Testing for dmacro module """

import unittest

from commonutil import dmacro


class Test_replace_macro(unittest.TestCase):
	def test_1(self):
		tpl_text = "${abc}"
		macro_map = {
				"abc": "-MACRO-",
		}
		result = dmacro.replace_macro(tpl_text, macro_map, False)
		self.assertEqual(result, "-MACRO-")

	def test_2(self):
		tpl_text = "we ${abc} the ${world_muz}"
		macro_map = {
				"abc": "-MACRO-",
				"world_muz": "X=WORLD",
		}
		result = dmacro.replace_macro(tpl_text, macro_map, False)
		self.assertEqual(result, "we -MACRO- the X=WORLD")

	def test_3(self):
		tpl_text = "we ${abc} the ${world_muz}}period"
		macro_map = {
				"abc": "-MACRO-",
				"world_muz": "X=WORLD",
		}
		result = dmacro.replace_macro(tpl_text, macro_map, False)
		self.assertEqual(result, "we -MACRO- the X=WORLD}period")

	def test_4(self):
		tpl_text = "we ${abc} the ${world_muz}}period ${lost}."
		macro_map = {
				"abc": "-MACRO-",
				"world_muz": "X=WORLD",
		}
		result = dmacro.replace_macro(tpl_text, macro_map, False)
		self.assertEqual(result, "we -MACRO- the X=WORLD}period .")

	def test_5(self):
		tpl_text = "we ${abc} the ${world_muz}}period ${lost}."
		macro_map = {
				"abc": "-MACRO-",
				"world_muz": "X=WORLD",
		}
		result = dmacro.replace_macro(tpl_text, macro_map, True)
		self.assertEqual(result, "we -MACRO- the X=WORLD}period ${lost}.")


if __name__ == '__main__':
	unittest.main()

# vim: ts=4 sw=4 ai nowrap
