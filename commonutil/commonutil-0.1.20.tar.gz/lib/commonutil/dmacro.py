# -*- coding: utf-8 -*-
""" 錢字符號為前置字串的巨集處理 / Dollar-sign prefixed macro processing """

import re

_MACROKEY_TRAP = re.compile('\$\{([a-zA-Z0-9_]+)\}')


def replace_macro(tpl_text, macro_map, placeholder_for_empty_macro=True):
	# type: (str, Dict[str, str], bool) -> str
	"""
	進行字串巨集替換

	Perform macro content substitute

	Args:
		tpl_text: 樣板文字 / Template text contains macro tags
		macro_map: 巨集值對應字典 / Content map of macro
		placeholder_for_empty_macro=True: 是否使用巨集鍵作為找不到巨及對應值時的值 / Use macro key for content of macro content not reachable from content map
	Return:
		取代巨集後的字串 / Resulted text of macro replacement
	"""
	result_q = []
	last_stop = 0
	m = _MACROKEY_TRAP.search(tpl_text)
	while m is not None:
		aux = tpl_text[last_stop:m.start()]
		result_q.append(aux)
		aux = macro_map.get(m.group(1))
		if aux is None:
			if placeholder_for_empty_macro:
				result_q.append(m.group(0))
		else:
			result_q.append(aux)
		last_stop = m.end()
		m = _MACROKEY_TRAP.search(tpl_text, last_stop)
	result_q.append(tpl_text[last_stop:])
	return "".join(result_q)


# vim: ts=4 sw=4 ai nowrap
