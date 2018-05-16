# -*- coding: utf-8 -*-
""" 基於檔案的時戳衍生 / Time-stamp from file attributes """

# 注意: 這個模組參考到了其他 commonutil 內的模組。
# 當製作 commonutil 模組時如果引用此模組，必須小心不要製造出遞迴的參考。
# Caution: as this module includes other modules from commonutil package.
# be careful, do not make circular reference if building commonutil module base on this module.

import os
import math
import time
import datetime
import logging

from commonutil.convert import to_bool
from commonutil.convert import to_integer
from commonutil.ticktock import get_tz_offset_info
from commonutil.pathtag import parse_template as parse_ptag_template
from commonutil.pathtag import replace as replace_ptag
from commonutil.fetch import get_by_keys

_log = logging.getLogger(__name__)

_DEFAULT_TIMETAG = (
		1970,
		1,
		1,
		0,
		0,
		0,
)


class NoopBuilder(object):
	""" 總是傳回預設的 TimeTag / Always result in default time-tag """

	def build(self, current_filepath, filename_regxmobj, pathname_regxmobj, *args, **kwds):  # pylint: disable=unused-argument
		# type: (str, re.MatchObject, re.MatchObject) -> datetime.datetime
		"""
		依據設定值取出 TimeTag / Build time tag according to configuration

		Args:
			current_filepath - 目前檔案路徑
			filename_regxmobj: 比對狀況物件，檔案部份 (re.MatchObject) / Match object of file name
			pathname_regxmobj: 比對狀況物件，路徑部份 (re.MatchObject) / Match object of path (folder) name

		Return:
			表示 TimeTag 的 datetime.datetime 物件 / Result datetime.datetime object representing time-tag
		"""
		# TODO: 註: 儘可能在這個地方保持最完整的 method prototype
		return datetime.datetime(*_DEFAULT_TIMETAG)


def _ptag_substitude(rulename, ruleobj, parm_ptag_replace, default_value=None):
	""" (internal) 進行 PathTag Match Rule 的轉換 / Perform PathTag match rule substitude

	Args:
		rulename: 規則名稱 (顯示在轉換失敗的 log 中) / Rule name (use in log of failed substitude)
		ruleobj: 規則物件 / Rule object
		parm_ptag_replace: 用做呼叫 pathtag.replace() 函數的參數集 / Parameter tuple for invoking pathtag.replace()
		default_value=None: 預設值 / Default value
	Return:
		轉換後的數值 / Translated value
	"""
	if ruleobj is None:
		return default_value
	v = replace_ptag(ruleobj, *parm_ptag_replace)
	if v is not None:
		try:
			return int(v)
		except Exception as e:
			_log.exception("cannot convert match rule with %r: %r (%r)", rulename, v, e)
	return default_value


class PathTagBuilder(NoopBuilder):
	""" 基於 Path Tag 產生 TimeTag / Build time-tag based on path-tag """

	def __init__(self,
					year_4d_rule=None,
					year_2d_rule=None,
					month_rule=None,
					day_rule=None,
					hour_rule=None,
					minute_rule=None,
					second_rule=None,
					baseoffset_sec=None,
					labeloffset_sec=None,
					period_sec=None,
					timezone_feedback=False,
					*args,
					**kwds):  # pylint: disable=too-many-arguments
		# type: (str, str, str, str, str, str, str, Any, Any, Any, Any) -> None
		"""
		Args:
			year_4d_rule=None: 四位數年份的來源規則，與 year_2d_rule 擇一給定 / Rule of 4-digit year (only one of year_4d_rule or year_2d_rule shall be given)
			year_2d_rule=None: 二位數年份的來源規則，前面會冠上 20 作為前兩位數，也就是產生的年份為 20xx 年，與 year_4d_rule 擇一給定 / Rule of 2-digit year (only one of year_{4d, 2d}_rule shall given)
			month_rule=None: 月份的來源規則，未給定時使用預設值 1 / Rule of month. Default to 1 if not given.
			day_rule=None: 日的來源規則，未給定時使用預設值 1 / Rule of day. Default to 1 if not given.
			hour_rule=None: 時的來源規則，未給定時使用預設值 0 / Rule of hour. Default to 0 if not given.
			minute_rule=None: 分的來源規則，未給定時使用預設值 0 / Rule of minute. Default to 0 if not given.
			second_rule=None: 秒的來源規則，未給定時使用預設值 0 / Rule of second. Default to 0 if not given.
			baseoffset_sec=None: 產生的時間標記的起點秒數，預設為 0 / Base offset of time-tag sequence. Default to 0 if not given.
			labeloffset_sec=None: 產生的時間標記的標記偏移秒數，預設為 0 / Label (Time-tag) offset to time frame. Default to 0 if not given.
			period_sec=None: 時間週期的長度 / Period in seconds
			timezone_feedback=False: 是否在計算時進行時區的回饋 / Time-zone feedback on computation
		"""
		super(PathTagBuilder, self).__init__(*args, **kwds)
		# {{{ time rules
		self.year_4d_rule = parse_ptag_template(year_4d_rule)
		self.year_2d_rule = parse_ptag_template(year_2d_rule)
		self.month_rule = parse_ptag_template(month_rule)
		self.day_rule = parse_ptag_template(day_rule)
		self.hour_rule = parse_ptag_template(hour_rule)
		self.minute_rule = parse_ptag_template(minute_rule)
		self.second_rule = parse_ptag_template(second_rule)
		# }}} time rules
		self.mtime_baseoffset_sec = to_integer(baseoffset_sec, 0)
		self.mtime_labeloffset_sec = to_integer(labeloffset_sec, 0)
		self.mtime_period_sec = to_integer(period_sec)
		self.mtime_timezone_feedback = to_bool(timezone_feedback, False)

	def build(self, current_filepath, filename_regxmobj, pathname_regxmobj, *args, **kwds):  # pylint: disable=too-many-locals
		"""
		依據設定值取出 TimeTag / Build time tag according to configuration

		Args:
			current_filepath - 目前檔案路徑
			filename_regxmobj: 比對狀況物件，檔案部份 (re.MatchObject) / Match object of file name
			pathname_regxmobj: 比對狀況物件，路徑部份 (re.MatchObject) / Match object of path (folder) name
		Return:
			表示 TimeTag 的 datetime.datetime 物件 / Result datetime.datetime object representing time-tag
		"""
		year, month, day, hour, minute, second, = _DEFAULT_TIMETAG
		if self.mtime_period_sec is None:
			file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(current_filepath) - self.mtime_baseoffset_sec + self.mtime_labeloffset_sec)
		else:
			if self.mtime_timezone_feedback:
				utc_offset_feedback, _tzname, = get_tz_offset_info()
			else:
				utc_offset_feedback = 0
			aux = (math.floor((os.path.getmtime(current_filepath) - utc_offset_feedback - self.mtime_baseoffset_sec) / self.mtime_period_sec) *
					self.mtime_period_sec) + self.mtime_labeloffset_sec + utc_offset_feedback
			file_mtime = datetime.datetime.fromtimestamp(aux)
		parm_ptag_replace = (
				filename_regxmobj,
				pathname_regxmobj,
				file_mtime,
		)
		# {{{ run replacement
		if self.year_4d_rule is not None:
			year = _ptag_substitude("year-4d", self.year_4d_rule, parm_ptag_replace, year)
		elif self.year_2d_rule is not None:
			year = 2000 + _ptag_substitude("year-2d", self.year_2d_rule, parm_ptag_replace, year - 2000)
		month = _ptag_substitude("month", self.month_rule, parm_ptag_replace, month)
		day = _ptag_substitude("day", self.day_rule, parm_ptag_replace, day)
		hour = _ptag_substitude("hour", self.hour_rule, parm_ptag_replace, hour)
		minute = _ptag_substitude("minute", self.minute_rule, parm_ptag_replace, minute)
		second = _ptag_substitude("second", self.second_rule, parm_ptag_replace, second)
		# }}} run replacement
		return datetime.datetime(year, month, day, hour, minute, second)


class FileTimeBuilder(NoopBuilder):
	""" 利用檔案修改時間產生 TimeTag / Build time-tag with file modification time """

	def __init__(self, filetime_rule, min_period, base_offset, label_offset, *args, **kwds):
		# type: (str, int, int)
		"""
		Args:
			filetime_rule: 使用到的時間元素 (字母 YMDhms 分別表示年月日時分秒) / Time element to apply (YMDhms represents year, month, day, hour, minute and second respectively)
			min_period: 最小時間週期 / Minimum period of time-tag series
			base_offset: 時序起點的偏移秒數 / Offset seconds to beginning of time-tag series
			label_offset: 標記的偏移秒數 / Offset seconds from beginning of time frame to time-tag
		"""
		super(FileTimeBuilder, self).__init__(*args, **kwds)
		self.filetime_rule = str(filetime_rule)
		self.min_period = to_integer(min_period, None)
		self.base_offset = to_integer(base_offset, 0)
		self.label_offset = to_integer(label_offset, 0)
		if (self.min_period is not None) and (self.min_period < 1):
			self.min_period = None

	def build(self, current_filepath, *args, **kwds):  # pylint: disable=arguments-differ
		"""
		依據設定值取出 TimeTag / Build time tag according to configuration

		Args:
			current_filepath - 目前檔案路徑
		Return:
			表示 TimeTag 的 datetime.datetime 物件 / Result datetime.datetime object representing time-tag
		"""
		year, month, day, hour, minute, second, = _DEFAULT_TIMETAG
		# {{{ compute time-tag
		time_start = time.localtime(0)
		filetstamp = os.path.getmtime(current_filepath)
		if self.min_period is not None:
			if time_start[3] == 8:
				filetstamp = (math.floor((filetstamp + 28800 - self.base_offset) / self.min_period) * self.min_period) + self.label_offset - 28800
			else:
				filetstamp = (math.floor((filetstamp - self.base_offset) / self.min_period) * self.min_period) + self.label_offset
		filetime = datetime.datetime.fromtimestamp(filetstamp)
		# }}} compute time-tag
		_log.debug("filetime: %r", filetime)
		r = self.filetime_rule
		if 'Y' in r:
			year = filetime.year
		if 'M' in r:
			month = filetime.month
		if 'D' in r:
			day = filetime.day
		if 'h' in r:
			hour = filetime.hour
		if 'm' in r:
			minute = filetime.minute
		if 's' in r:
			second = filetime.second
		return datetime.datetime(year, month, day, hour, minute, second)


def parse_build_rule(cmap):
	# type: (Dict[str, Any]) -> NoopBuilder
	"""
	解析建立 Time-tag 的規則

	Parse time-tag build rule from dictionary

	Args:
		cmap: dict object contains build rule configuration
	Return:
		從檔案屬性建立 Time-tag 的 Builder 物件 / Object to build time-tag from file attributes
	"""
	if ('year_4d' in cmap) or ('year_2d' in cmap):
		return PathTagBuilder(
				cmap.get('year_4d'), cmap.get('year_2d'), cmap.get('month'), cmap.get('day'), cmap.get('hour'), cmap.get('minute'), cmap.get('second'),
				cmap.get('mtime-base-offset'), cmap.get('mtime-label-offset'), get_by_keys(cmap, (
						'mtime-period',
						'mtime-freq',
				)), cmap.get('mtime-timezone-feedback'))
	elif 'use-file-time' in cmap:
		return FileTimeBuilder(cmap.get('use-file-time'), get_by_keys(cmap, (
				'period',
				'frequency',
		)), cmap.get('base-offset'), cmap.get('label-offset'))
	return NoopBuilder()


# vim: ts=4 sw=4 ai nowrap
