# -*- coding: utf-8 -*-
""" 應用程式輔助函式 / Application helper functions """

import os
import re
import signal
import syslog
import logging
_log = logging.getLogger(__name__)


def prepare_syslog(app_name, config_filepath=None):
	# type: (str, str) -> None
	"""
	依據設定檔檔名設定要在 syslog 中顯示的應用程式名稱

	Setup syslog according to given application name and configuration file name

	Args:
		app_name: 應用程式名稱 / Application name
		config_filepath=None: 設定檔案路徑 / Path of configuration file
	"""
	# {{{ 決定 log 標示名稱
	if config_filepath is None:
		logging_name = app_name
	else:
		logging_name = os.path.basename(config_filepath)
		logging_name = re.match("^([a-zA-Z0-9_-]+)", logging_name)
		if logging_name is None:
			logging_name = app_name
		else:
			logging_name = ''.join((
					app_name,
					'.',
					logging_name.group(1),
			))
	# }}} 決定 log 標示名稱
	syslog.openlog(logging_name, syslog.LOG_PID | syslog.LOG_PERROR, syslog.LOG_DAEMON)


_APPLICATION_STOP_CALLABLE = None


def _termination_signal_handler(signum, frame):  # pylint: disable=unused-argument
	""" (internal) UNIX Signal 處理器 / UNIX Signal handler
	"""
	if _APPLICATION_STOP_CALLABLE is not None:
		_APPLICATION_STOP_CALLABLE()
	_log.info("Received Stop Signal.")


def regist_terminate_signal(stop_callable=None, handle_sigterm=False):
	# type: (Callable[[], None], bool) -> None
	"""
	註冊終止訊號處理器

	Register terminate signal handler call-able

	Args:
		stop_callable=None: 發生終止訊號時要執行的函式 / Call-able object or function to invoke on received terminate signal
		handle_sigterm=False: 是否也要攔截 SIGTERM 訊號 / Handles SIGTERM signal
	"""
	global _APPLICATION_STOP_CALLABLE
	_APPLICATION_STOP_CALLABLE = stop_callable
	signal.signal(signal.SIGINT, _termination_signal_handler)
	if handle_sigterm:
		signal.signal(signal.SIGTERM, _termination_signal_handler)


def setup_hourly_rotated_logging_file(base_log_path, logging_level=logging.INFO, backup_count=120):
	# type: (str, int, int) -> None
	"""
	設定每小時更換檔名的檔案紀錄方式

	Setup logging file with hourly rotating

	Args:
		base_log_path: 紀錄檔的路徑 / Path of logging file
		logging_level=logging.INFO: 紀錄層級 / Logging level
		backup_count=120: 要保留的檔案數量 / Number of kept logging file
	"""
	from logging.handlers import TimedRotatingFileHandler as TimedRotatingFileLoggingHandler
	root_logger = logging.getLogger()
	handler = TimedRotatingFileLoggingHandler(base_log_path, when='H', encoding='utf-8', backupCount=backup_count)
	formatter = logging.Formatter("%(asctime)s[%(levelname)s]%(name)s:%(message)s", "%H:%M:%S")
	handler.setFormatter(formatter)
	_log.info("write log to %r with hourly rotating", base_log_path)
	root_logger.addHandler(handler)
	root_logger.setLevel(logging_level)
	_log.info("switched logging handler")


# vim: ts=4 sw=4 ai nowrap
