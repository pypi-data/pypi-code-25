# -*- coding: utf-8 -*-
""" 狀態報告檔案類別 / Status report file classes """

import time
import logging
_log = logging.getLogger(__name__)


def _text_fmt(t, args, kwds):
	""" (internal) 將文字格式化 / Format text
	"""
	try:
		if args:
			aux = t % args
			t = aux
		elif kwds:
			aux = t % kwds
			t = aux
	except Exception as e:
		_log.exception("cannot format given text: %r", e)
	return t


class _RuntimeStatusReport_FlowContext(object):
	def __init__(self, report_object, flow_name, *args, **kwds):
		# type: (RuntimeStatusReport, str) -> None
		super(_RuntimeStatusReport_FlowContext, self).__init__(*args, **kwds)
		self.report_object = report_object
		self.flow_name = flow_name

	def __enter__(self):
		self.report_object.enter_flow(self.flow_name)
		return self.report_object

	def __exit__(self, type_obj, except_value, traceback_obj):
		self.report_object.leave_flow()


class RuntimeStatusReport(object):
	""" 執行時期狀態報告檔 / Runtime status report file """

	def __init__(self, report_path, *args, **kwds):
		# type: (str) -> None
		"""
		Args:
			report_path: 報告檔案路徑 / Path of status report file
		"""
		super(RuntimeStatusReport, self).__init__(*args, **kwds)
		self.report_path = report_path
		self.flow_stack = []
		self.flow_text = "-"

	def _flow_updated(self):
		self.flow_text = "/".join(self.flow_stack) if self.flow_stack else "-"

	def enter_flow(self, flow_name):
		# type: (str) -> None
		"""
		進入一個流程

		Enter a flow with given name

		Args:
			flow_name: 流程名稱 / Flow name
		"""
		self.flow_stack.append(flow_name)
		self._flow_updated()
		self.update("enter flow [%r]", flow_name)

	def leave_flow(self):
		# type: () -> None
		"""
		離開流程

		Left latest entered flow
		"""
		f = None
		try:
			f = self.flow_stack.pop()
		except Exception:
			pass
		self._flow_updated()
		self.update("leaved flow [%r]", f)

	def flow(self, flow_name, *args, **kwds):
		# type: (str, *str, **str) -> ContextManager
		"""
		進行一個流程，搭配 with 關鍵字使用

		Going to run a flow. Use with `with` keyword.

		Args:
			flow_name: 流程名稱 / Flow name
		"""
		flow_name = _text_fmt(flow_name, args, kwds)
		return _RuntimeStatusReport_FlowContext(self, flow_name)

	def update(self, msg, *args, **kwds):
		# type: (str, *str, **str) -> None
		"""
		更新狀態文字，會打開指定的狀態檔並寫入

		Open status file and update status text. Close file after update completed.

		Args:
			msg: 狀態文字 / Status text
		"""
		msg = _text_fmt(msg, args, kwds)
		try:
			current_tstamp = int(time.time())
			with open(self.report_path, "w") as fp:
				fp.write("%d: [%s]\n" % (
						current_tstamp,
						self.flow_text,
				))
				fp.write(msg)
				fp.write("\n--\n")
		except Exception as e:
			_log.exception("cannot write status update file: %r", e)


# vim: ts=4 sw=4 ai nowrap
