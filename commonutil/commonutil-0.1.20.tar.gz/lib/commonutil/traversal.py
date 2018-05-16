# -*- coding: utf-8 -*-
""" 資料遊走輔助函式 / Structured content traversal routines """


def iter_nested_text_list(l, indent_text="\t"):
	# type: (Iterator[str], str) -> Generator[str]
	"""
	將多層的字串串列物件攤平為單層的字串串列物件

	Flatten multiple-level (nested) text list object into one-level text list

	Args:
		l: 要攤平的字串串列物件 / text list object to be flatten
		indent_text="\t": 縮排文字 / text to indent content of nested level

	Yield:
		依據串列層次進行縮排調整的字串
	"""
	for t in l:
		if t is None:
			yield None
		elif isinstance(t, basestring):
			yield t
		else:
			for u in iter_nested_text_list(t, indent_text):
				yield None if (u is None) else (indent_text + u)


class NestedTextListFlattener(object):
	""" 將多層的文字輸出為單層的遊走器 """

	def __init__(self, indent_text="\t", container_class=None, *args, **kwds):
		# type: (str, Callable[[Generator[str]], Any]) -> None
		"""
		建構子 / Constructor

		Args:
			indent_text="\t": 縮排文字 / text to indent content of nested level
			container_class=None: 儲存輸出用的容器類別，當 None 時直接傳回 Generator 物件 / Container class to keep result data. Result into Generator object if None is given.
		"""
		super(NestedTextListFlattener, self).__init__(*args, **kwds)
		self.indent_text = indent_text
		self.container_class = container_class

	def __call__(self, *args):
		g = iter_nested_text_list(args, self.indent_text)
		return g if (self.container_class is None) else self.container_class(g)


# vim: ts=4 sw=4 ai nowrap
