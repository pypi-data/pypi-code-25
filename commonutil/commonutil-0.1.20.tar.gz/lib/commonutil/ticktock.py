# -*- coding: utf-8 -*-
""" 時間相關輔助函式 / Time related support routines """

import sys
import time
import datetime
import logging
_log = logging.getLogger(__name__)

_tz_offset_info_cached = None
_tz_offset_info_cache_time = 0


def get_tz_offset_info(use_cached_info=True):
	# type: (bool) -> Tuple[int, str]
	"""
	取出時區偏移資訊，當呼叫端允許時使用快取，快取資料會留存 1800 秒 (30 分鐘) 以處理日光節約時間轉換的議題

	Get time-zone offset information.
	Will use cached data if acceptable. The cache will keep 1800 seconds (half hour) for DST transition.

	Args:
		use_cached_info=True: 是否要使用快取的結果，預設為 (True) 使用 / use cache or not

	Return:
		型式為 (偏移秒數, 時區名稱) 的 tuple

		Tuple in (offset-seconds, timezone-name,) form
	"""
	global _tz_offset_info_cached
	# {{{ 使用 cache 資料如果呼叫端允許時
	if use_cached_info:
		global _tz_offset_info_cache_time
		current_time = time.time()
		if (current_time - _tz_offset_info_cache_time) < 1800:
			_tz_offset_info_cache_time = current_time
			if _tz_offset_info_cached is not None:
				return _tz_offset_info_cached
	# }}} 使用 cache 資料如果呼叫端允許時
	# {{{ determine tz-utc-offset and tz-name
	tz_name_ndst, tz_name_dst, = time.tzname  # pylint: disable=unbalanced-tuple-unpacking
	localtm = time.localtime()
	if localtm.tm_isdst == 0:
		host_tz_utcoffset_second = time.timezone
		host_tz_name_raw = tz_name_ndst
	else:
		host_tz_utcoffset_second = time.altzone
		host_tz_name_raw = tz_name_dst
	# }}} determine tz-utc-offset and tz-name
	# {{{ generate time zone text
	try:
		host_tz_name = host_tz_name_raw.decode()
	except Exception:
		host_tz_name = None
	# -- should success here in most case
	if host_tz_name is None:
		try:
			host_tz_name = host_tz_name_raw.decode(sys.stdout.encoding)
		except Exception:
			host_tz_name = None
		if host_tz_name is None:
			host_tz_symbol = "" if (host_tz_utcoffset_second < 0) else "+"
			host_tz_hh = int(host_tz_utcoffset_second / 3600)
			host_tz_name = "UTC%s%02d" % (
					host_tz_symbol,
					host_tz_hh,
			)
	# }}} generate time zone text
	_tz_offset_info_cached = (
			host_tz_utcoffset_second,
			host_tz_name,
	)
	return _tz_offset_info_cached


def timedelta_to_seconds(d):
	# type: (datetime.timedelta) -> int
	"""
	將給定的 datetime.timedelta 物件內含秒數計算出來傳回

	Calculate seconds in given datetime.timedelta object.

	Args:
		d: 要取秒數值的 datetime.timedelta 物件

	Return:
		給定的 datetime.timedelta 內含之秒數值

		Total seconds in given datetime.timedelta object.
	"""
	return (d.days * 86400 + d.seconds)


def CYCLE_PRECISION_SECOND(dt):
	# type: (datetime.datetime) -> datetime.datetime
	""" (Cycle Precision Function) 週期精確度為秒的時間點調整函式 / Date time value adjustment function for run_timeseries_loop
	"""
	return dt.replace(microsecond=0, tzinfo=None)


def CYCLE_PRECISION_MINUTE(dt):
	# type: (datetime.datetime) -> datetime.datetime
	""" (Cycle Precision Function) 週期精確度為分的時間點調整函式 / Date time value adjustment function for run_timeseries_loop
	"""
	return dt.replace(second=0, microsecond=0, tzinfo=None)


# pylint: disable=too-many-arguments,too-many-locals
def run_timeseries_loop(cycling_callable,
						housekeeping_callable=None,
						tstamp_storage_path=None,
						invoke_period=1800,
						cycle_period=3600,
						housekeeping_period=7200,
						max_delay=120,
						cycle_precision=CYCLE_PRECISION_MINUTE):
	# type: (Callable[[datetime.datetime, datetime.datetime], bool], Callable[[], None], str, int, int, int, int, Callable[[datetime.datetime], datetime.datetime]) -> None
	"""
	執行掃描時間序列的迴圈，指定的函數物件會在指定時間後被呼叫，兩個分別代表時間區段起點與終點之時間點會被傳入指定函數。

	Run a loop to call given function (or call-able) periodically.
	Two date-time objects will be passed into given function. The objects indicates segments in continues time flow.

	- 注意: 時間序列精度 (cycle_precision) 的值應小於掃描頻率 (invoke_period) 的值，由於精度值為程式指定，因此呼叫此函式的程式碼應該自行檢查

	- Caution: the cycle precision adjust by precision function should smaller than invoke period.

	Args:
		cycling_callable: 迴圈函數，函數原型為 (bool) cycling_callable(range_s, range_e) 當回傳值為 False 時將結束迴圈 / Call-able to be invoke in given cycle. The function prototype is (bool) cycling_callable(range_s, range_e). The loop will terminate when return value of given call-able is False.
		housekeeping_callable=None: 定期自動檢點函數 / House-keeping call-able
		tstamp_storage_path=None: 儲存 time-stamp 值的檔案的路徑 / File path to keep progress.
		invoke_period=1800: 掃描週期 / Scan period to check if next invoke should take place
		cycle_period=3600: 每次掃描要延展的長度，作為呼叫 cycling_callable 的參數時間的長度 / Time span of the arguments for invoking cycle call-able
		housekeeping_period=7200: 執行檢點作業的週期 / Period to perform house keeping
		max_delay=120: 啓動時可接受的最大延誤時間，啟動時距離上次結束如果已經超過給定時間，則直接使用目前時間減去此延誤時間作為時間區段的起始時間 / Max acceptable delay between invoking
		cycle_precision=CYCLE_PRECISION_MINUTE: 時間序列精度 / Time value adjustment function
	"""
	last_housekeeping_tstamp = 0
	prev_tstamp = 0
	# {{{ 確保 house keeping 相關參數是可以執行後續動作的
	if housekeeping_period is None:
		housekeeping_callable = None
		housekeeping_period = 7200
	# }}} 確保 house keeping 相關參數是可以執行後續動作的
	# {{{ load time-stamp from previous run
	if tstamp_storage_path is not None:
		try:
			with open(tstamp_storage_path, "r") as fp:
				l = fp.readline()
			prev_tstamp = int(l.strip())
		except Exception:
			prev_tstamp = 0
	# }}} load time-stamp from previous run
	current_tstamp = time.time()
	range_s = None
	range_e = cycle_precision(datetime.datetime.fromtimestamp(max((current_tstamp - max_delay), prev_tstamp)))
	while True:
		current_tstamp = time.time()
		range_s = range_e
		range_e = cycle_precision(datetime.datetime.fromtimestamp(current_tstamp + cycle_period))
		# {{{ check if range value reasonable (should not happen unless having big clock drift during iteration, check for safe)
		if not (range_s < range_e):
			range_s, range_e, = (range_e, range_s)
			idle_seconds = timedelta_to_seconds(range_e - range_s)
			if idle_seconds > 0:
				time.sleep(idle_seconds)
			else:
				time.sleep(1)
			continue
		# }}} check if range value reasonable
		# run cycling function
		ret = cycling_callable(range_s, range_e)
		# {{{ save time-stamp
		if tstamp_storage_path is not None:
			try:
				with open(tstamp_storage_path, "w") as fp:
					fp.write(str(current_tstamp))
					fp.write("\n")
			except Exception as e:
				_log.warning("cannot write into time-stamp storage (path=%r): %r", tstamp_storage_path, e)
		# }}} save time-stamp
		if not ret:
			return
		# {{{ do house keeping
		if (last_housekeeping_tstamp + housekeeping_period) < current_tstamp:
			if housekeeping_callable is not None:
				housekeeping_callable()
			last_housekeeping_tstamp = current_tstamp
		# }}} do house keeping
		prev_tstamp = current_tstamp
		# {{{ idle for next invoke
		idle_seconds = invoke_period - (time.time() - prev_tstamp)
		if idle_seconds > 0:
			time.sleep(idle_seconds)
		# }}} idle for next invoke


# vim: ts=4 sw=4 ai nowrap
