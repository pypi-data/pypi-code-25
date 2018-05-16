# -*- coding: utf-8 -*-
""" 數值儲存用類別 / Value container classes """

from collections import namedtuple, OrderedDict
import logging
_log = logging.getLogger(__name__)


class CountDownValuePopper(object):
	def __init__(self, initial_count, initial_pop, *pop_rules, **kwds):
		# type: (int, int, *Tuple[int, Any]) -> None
		"""
		依據已取值次數回傳不同的數值

		Return different value according to number of pops

		Args:
			initial_count: 初始的計數值 / Initial count number
			initial_pop: 最一開始的回傳值 / Initial popped value
			*pop_rules: 以 (bound, pop_value,) 型式 tuple 構成的各計數起對應的回傳值 / Pop rule formed by tuple in (bound, pop_value,) format
		"""
		super(CountDownValuePopper, self).__init__(**kwds)
		self.c = initial_count
		self.base_pop = initial_pop
		self.pop_rules = pop_rules

	def pop(self):
		# type: () -> Any
		prev_c = self.c
		self.c = prev_c - 1
		result = self.base_pop
		for bound_value, result_pop, in self.pop_rules:
			if prev_c > bound_value:
				return result
			result = result_pop
		return result

	def __call__(self, *args, **kwds):
		return self.pop()


ContentListEntity = namedtuple("ContentListEntity", (
		"content_key",
		"content_list",
))


class OrderedKeyContentList(object):
	""" 有順序的有鍵的值所構成的串列 / List of content with key """

	def __init__(self, *args, **kwds):
		super(OrderedKeyContentList, self).__init__(*args, **kwds)
		self.l = []
		self.m = {}

	def add(self, k, content):
		# type: (Any, Any) -> None
		"""
		增加給定的鍵值組

		Add given key-value pair. If given key does not existed in this container a list container will be created for keeping given value.

		Args:
			k: 給定值所屬的鍵 / Key value of given content
			content: 給定值 / Value of given content
		"""
		if k not in self.m:
			aux = ContentListEntity(k, list())
			self.l.append(aux)
			self.m[k] = aux
		self.m[k].content_list.append(content)

	def __iter__(self):
		return iter(self.l)


class LayeredObject(object):
	def __init__(self, *args, **kwds):  # pylint: disable=unused-argument
		# type: (*Any) -> None
		"""
		分層的物件容器，由最早加入的物件中 (索引零) 找尋所要存取的屬性 (attribute) 值，為 None 的值會被略過。
		屬性應避免使用底線 ("_") 開頭，所有尋找到的屬性會試圖利用類別方法 (class method) _merge_ATTRIBUTE 加以合併，如果沒有定義該類別方法，則取最晚加入的非 None 值。
		當所有加入的物件都沒有指定的屬性值，則會產生 AttributeError 例外。如果可以找到值但都為 None 的話，則傳回 None 值。

		Layered object container. Attributes are searched from earliest (Index 0) and None value will be skipped.
		Attribute names should not prefixed with underline ("_"). Searched value will be merge by invoking class method _merge_ATTRIBUTE.
		The latest attribute value of object will be return if no such method defined.
		An AttributeError exception will be raised if none of contained objects has value of desired attribute.

		Args:
			*args: 要置入的物件 / Objects to placed into this container
		"""
		super(LayeredObject, self).__init__()
		self._layered = list(args)

	def append(self, obj):
		# type: (Any) -> None
		"""
		將給定的物件放到搜尋順序的最後方

		Append given object.

		Args:
			obj: 要加入的物件 / object to append
		"""
		self._layered.append(obj)

	def _get_merged_content(self, name):
		candidate = []
		has_property = False
		for c in self._layered:
			try:
				v = getattr(c, name)
				if v is not None:
					candidate.append(v)
				has_property = True
			except AttributeError:
				pass
		if not has_property:
			raise AttributeError(name)
		if not candidate:
			return None
		for c, f_name, in (
				(
						self._layered[-1].__class__,
						"_merge_" + name,
				),
				(
						candidate[-1].__class__,
						"_merge",
				),
		):
			merge_f = getattr(c, f_name, None)
			if merge_f:
				break
		return candidate[-1] if (merge_f is None) else merge_f(*candidate)

	def __getattr__(self, name):
		return self._get_merged_content(name)


class SealableOrderedDict(OrderedDict):
	"""
	可固定已有的鍵值不被後續程序變更的有序字典物件

	A seal-able ordered dictionary
	"""

	def __init__(self, *args, **kwds):
		super(SealableOrderedDict, self).__init__(*args, **kwds)
		self._sealed_keys = None

	def seal(self):
		# type: () -> None
		"""
		固定已有的鍵值，針對既有鍵的後續的變更作業會丟出 KeyError 例外

		Seal existed key-value pair. Later modification will resulted in KeyError exception.
		"""
		self._sealed_keys = frozenset(self.iterkeys())

	def unseal(self):
		# type: () -> None
		"""
		解除鍵值的固定

		Remove key-value seal.
		"""
		self._sealed_keys = None

	def _watch_sealed_key(self, key):
		""" (internal) a KeyError will be raise if a sealed key is given """
		if self._sealed_keys and (key in self._sealed_keys):
			raise KeyError("given key is sealed: %r" % (key, ))

	def __setitem__(self, key, *args, **kwds):
		self._watch_sealed_key(key)
		super(SealableOrderedDict, self).__setitem__(key, *args, **kwds)

	def __delitem__(self, key, *args, **kwds):
		self._watch_sealed_key(key)
		super(SealableOrderedDict, self).__delitem__(key, *args, **kwds)

	def clear(self):
		if self._sealed_keys:
			raise ValueError("cannot clear() on a sealed dictionary.")
		super(SealableOrderedDict, self).clear()
		self._sealed_keys = None


class AppendToListDecorator(object):
	""" 用來將被裝飾的語言物件存入一個串列的裝飾器類別 / Decorator to append decorated element into a list """

	def __init__(self, *args, **kwds):
		super(AppendToListDecorator, self).__init__(*args, **kwds)
		self._container = list()

	def __call__(self, decorating_target):
		self._container.append(decorating_target)
		return decorating_target

	def __iter__(self):
		return iter(self._container)


# vim: ts=4 sw=4 ai nowrap
