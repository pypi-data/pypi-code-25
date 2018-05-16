# -*- coding: utf-8 -*-
""" 路徑為基礎的標記或巨集支援 / Path-based Tag or Macro Support """

# 注意: 這個模組參考到了其他 commonutil 內的模組。
# 當製作 commonutil 模組時如果引用此模組，必須小心不要製造出遞迴的參考。
# Caution: as this module includes other modules from commonutil package.
# be careful, do not make circular reference if building commonutil module base on this module.

import re
import datetime

from commonutil.convert import to_text

_PTAG_TYPE_FILE = 1
_PTAG_TYPE_PATH = 2
_PTAG_TYPE_CURRENT = 3
_PTAG_TYPE_MTIME = 4
_PTAG_KEY_MAP = {
		'F': _PTAG_TYPE_FILE,
		'P': _PTAG_TYPE_PATH,
		'N': _PTAG_TYPE_CURRENT,
		'M': _PTAG_TYPE_MTIME,
}
_ptag_trap_regex = re.compile(u'([PFNM])\$((\{([0-9]+)\})|([0-9]))')


def parse_template(v):
	# type: (str) -> Any
	"""
	將輸入的檔名與路徑關鍵字代換字串轉換為後續供代換作業的物件

	Translate given string which contained path-tag macros into match object

	Args:
		v: 要轉換的代換字串 / Macro string
	Return:
		供代換作業使用的物件 / Match object for substitute operation
	"""
	if v is None:
		return None
	v = str(v)
	remain_s = 0
	remain_e = len(v)
	rule_q = []  # result container
	# {{{ search substitute keyword
	m = _ptag_trap_regex.search(v, remain_s, remain_e)
	while m is not None:
		# {{{ get text before rule-string
		left_e = m.start(0)
		if left_e > remain_s:
			rule_q.append(v[remain_s:left_e])
		# }}} get text before rule-string
		# {{{ create rule object
		try:
			type_code = _PTAG_KEY_MAP[str(m.group(1))]
			g_idx = m.group(4)
			if g_idx is None:
				g_idx = m.group(5)
			g_idx = int(g_idx)
			rule_q.append((
					type_code,
					g_idx,
			))
		except Exception as e:
			rule_q.append("?/ERR:%r/" % (e, ))
		# }}} create rule object
		remain_s = m.end(0)
		if remain_s < remain_e:
			m = _ptag_trap_regex.search(v, remain_s, remain_e)
		else:
			m = None
	# }}} search substitute keyword
	if remain_s < remain_e:
		rule_q.append(v[remain_s:remain_e])
	return rule_q if rule_q else None


def _datetime_prop_by_index(dtobj, idx):
	if idx == 1:
		return str(dtobj.year).zfill(4)
	elif idx == 2:
		return str(dtobj.month).zfill(2)
	elif idx == 3:
		return str(dtobj.day).zfill(2)
	elif idx == 4:
		return str(dtobj.hour).zfill(2)
	elif idx == 5:
		return str(dtobj.minute).zfill(2)
	elif idx == 6:
		return str(dtobj.second).zfill(2)
	return u'?/ERR:datetime-index/'


def replace(xtrule, f_mobj, p_mobj, filemtime_dtobj=None):
	# type: (Any, re.MatchObject, re.MatchObject, datetime.datetime) -> str
	"""
	執行檔名與路徑關鍵字代換字串作業

	Perform tag replacement by given match rule object

	Args:
		xtrule: 從 parse_time_tag_template() 函數取得的代換作業參數物件 / Match rule object get from parse_time_tag_template() function
		f_mobj: 檔案名稱的 regex match object / regex match object of file name
		p_mobj: 檔案路徑的 regex match object / regex match object of file path (folder part)
		filemtime_dtobj=None: 檔案的變更時間物件 (已經偏移完成) / datetime.datetime object of the file modify time (must shift to desired time zone before pass in)
	Return:
		經過代換的字串 / Result string
	"""
	result_q = []
	for xtitem in xtrule:
		elem = None
		# {{{ 決定字串片段 (elem)
		if isinstance(xtitem, tuple):
			try:
				subs_type, subs_idx, = xtitem
				if _PTAG_TYPE_FILE == subs_type:
					elem = f_mobj.group(subs_idx)
				elif _PTAG_TYPE_PATH == subs_type:
					elem = p_mobj.group(subs_idx)
				elif _PTAG_TYPE_CURRENT == subs_type:
					elem = _datetime_prop_by_index(datetime.datetime.now(), subs_idx)
				elif (_PTAG_TYPE_MTIME == subs_type) and (filemtime_dtobj is not None):
					elem = _datetime_prop_by_index(filemtime_dtobj, subs_idx)
			except Exception as _e:
				# elem = default_value
				elem = u"?/ERR:%r/" % (_e, )
		else:
			elem = xtitem
		# }}} 決定字串片段
		if (elem is not None) and (not isinstance(elem, unicode)):
			elem = to_text(elem, None)
		if elem is not None:
			result_q.append(elem)
	return u''.join(result_q) if result_q else None


# vim: ts=4 sw=4 ai nowrap
