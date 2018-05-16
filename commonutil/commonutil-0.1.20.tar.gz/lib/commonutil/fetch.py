# -*- coding: utf-8 -*-
""" 值擷取輔助函數 / Value fetch functions """

from itertools import izip


def get_by_keys(d, keys, default_value=None):
	# type: (Dict[Any, Any], List[Any], Optional[Any]) -> Any
	"""
	從給定的字典物件中依序利用指定的鍵串列取出值，傳回第一個非 None 的值。

	如果都沒有非 None 的值，或是鍵都不存在，那就傳回指定的預設值。

	Get value from given dictionary object and return first value which is not None.

	If all mapped value is None or none of key exists, return given default value.

	Args:
		d (dict): 要取值的字典物件 / Dictionary object to fetch value from
		keys (list of key): 指定的鍵構成的串列 / List of key to fetch value for
		default_value=None: 預設值 / Default value

	Return:
		第一個取得的值，或是當沒有辦法取得非 None 值時，傳回給定的預設值 / First non-None value mapped from given dictionary
	"""
	for k in keys:
		aux = d.get(k)
		if aux is not None:
			return aux
	return default_value


def get_attrs(obj, *args):
	# type: (Any, *str) -> Generator[Any]
	"""
	取得複數個物件中的屬性，循序傳回結果

	Get attribute from objects.

	Args:
		object: 要找尋屬性的物件 / Object to searching for attribute
		attr_name, default_value: 要找尋的屬性名稱字串與預設值 / Attribute name string and default values

	Yield:
		取出的屬性或預設值 / Fetched attribute value or default value
	"""
	for attr_name, default_val, in izip(iter(args), iter(args)):
		yield getattr(obj, attr_name, default_val)


def get_attrs_notzero(obj, *args):
	# type: (Any, *str) -> Generator[Any]
	"""
	取得複數個物件中的屬性，循序傳回結果。若取出值為 0 的話，則傳回預設值。

	Get attribute from objects. Yields default value if fetched value is 0.

	Args:
		object: 要找尋屬性的物件 / Object to searching for attribute
		attr_name, default_value: 要找尋的屬性名稱字串與預設值 / Attribute name string and default values

	Yield:
		取出的屬性或預設值 / Fetched attribute value or default value
	"""
	for attr_name, default_val, in izip(iter(args), iter(args)):
		v = getattr(obj, attr_name, 0)
		yield default_val if (v == 0) else v


def get_attrs_notnone(obj, *args):
	# type: (Any, *str) -> Generator[Any]
	"""
	取得複數個物件中的屬性，循序傳回結果。若取出值為 None 的話，則傳回預設值。

	Get attribute from objects. Yields default value if fetched value is None.

	Args:
		object: 要找尋屬性的物件 / Object to searching for attribute
		attr_name, default_value: 要找尋的屬性名稱字串與預設值 / Attribute name string and default values

	Yield:
		取出的屬性或預設值 / Fetched attribute value or default value
	"""
	for attr_name, default_val, in izip(iter(args), iter(args)):
		v = getattr(obj, attr_name, None)
		yield default_val if (v is None) else v


# vim: ts=4 sw=4 ai nowrap
