# -*- coding: utf-8 -*-
""" 常用例外類別 / Exception classes """


class OutOfLocationSet(Exception):
	"""
	表示所有給訂的位址已經嘗試過，但都無法成功進行操作

	All given location (address + port) is tried but none of them able to establish operation successfully
	"""

	def __init__(self, method_name, *args, **kwds):
		super(OutOfLocationSet, self).__init__(*args, **kwds)
		self.method_name = method_name

	def __str__(self):
		return "out of client locations for method: %r" % (self.method_name, )


# vim: ts=4 sw=4 ai nowrap
