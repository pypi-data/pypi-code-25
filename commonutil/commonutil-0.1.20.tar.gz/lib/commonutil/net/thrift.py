# -*- coding: utf-8 -*-
""" Thrift 支援函式 / Thrift helper routines """

import thread
from contextlib import closing
import logging

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from commonutil.exceptions import OutOfLocationSet

_log = logging.getLogger(__name__)


def _connect(client_cls, host, port, timeout=3000.0):
	transport = TSocket.TSocket(host, port)
	transport.setTimeout(timeout)
	transport = TTransport.TFramedTransport(transport)
	protocol = TBinaryProtocol.TBinaryProtocol(transport)
	client = client_cls(protocol)
	try:
		transport.open()  # connect
		server_tstamp = client.ping()
		_log.debug("server time-stamp: %r", server_tstamp)
		return (client, transport)
	except Exception as e:
		_log.error("failed on open connection to [%r:%r]: %r", host, port, e)
	try:
		transport.close()
	except Exception:
		pass
	return (None, None)


def _invoke(client, method_name, args, kwds):
	m = getattr(client, method_name)
	return m(*args, **kwds)


class ClusteredClient(object):
	def __init__(self, client_cls, location_set, timeout=3000.0, passthrough_exception=None, *args, **kwds):
		# type: (Callable[[TProtocolBase], Any], List[Tuple[str, int]], float, Tuple[Exception]) -> None
		"""
		一組作為叢集的終端物件

		Client object formed by cluster of server locations

		Args:
			client_cls: Thrift 資料類別物件 / Thrift client class object
			location_set: 由 (host, port,) 這組分別代表伺服器主機位址與通訊埠的 tuple 物件所構成的串列 / Sequence container of (host, port,) tuples
			timeout=3000.0: 預設的逾時微秒 (millisecond, 10^-3 seconds) / Default timeout for RPC operations
			passthrough_exception=None: 要直接通過不視為異常的例外 / Exceptions that will pass-through caller instead of try next server
		"""
		super(ClusteredClient, self).__init__(*args, **kwds)
		self.client_cls = client_cls
		self.location_set = location_set
		self._timeout = timeout
		self._passthrough_exception = passthrough_exception
		self._client = None
		self._transport = None
		self._lockobject = thread.allocate_lock()
		self._cached_invoker = {}

	@classmethod
	def _open_link(cls, host, port, timeout=3000.0):
		"""
		連線到遠端主機，預設時作為使用 TSocket + TFramedTransport 進行連線，並使用 TBinaryProtocol 作為編碼協定。
		可覆蓋這個類別方法來改變連線行為。

		Open connection of remote server.

		Args:
			host: 主機位址 / Server host address
			port: 通訊埠 / TCP port to server
			timeout=3000.0: 作業逾時微秒數 / Milliseconds to time-out

		Return:
			傳回 TTransport 與 TProtocol 物件所構成的 tuple / Tuple object build from TTransport and TProtocol objects
		"""
		transport = TSocket.TSocket(host, port)
		transport.setTimeout(timeout)
		transport = TTransport.TFramedTransport(transport)
		protocol = TBinaryProtocol.TBinaryProtocol(transport)
		return (transport, protocol)

	@classmethod
	def _check_client(cls, client):
		"""
		檢查終端物件是不是可以使用，預設使用 int64 ping() 介面，如要使用其他介面則需要覆蓋這個類別方法。

		Check of client object is usable

		Args:
			client: 要檢查的終端物件
		"""
		server_tstamp = client.ping()
		_log.debug("server time-stamp: %r", server_tstamp)

	@classmethod
	def _connect(cls, client_cls, host, port, timeout=3000.0):
		transport, protocol, = cls._open_link(host, port, timeout)
		client = client_cls(protocol)
		try:
			transport.open()  # connect
			cls._check_client(client)
			return (client, transport)
		except Exception as e:
			_log.error("failed on open connection to [%r:%r]: %r", host, port, e)
		try:
			transport.close()
		except Exception:
			pass
		return (None, None)

	def connect(self):
		# type: () -> ContextManager
		"""
		傳回這個物件的 Context Manager 以用來確保操作後都有正常關閉連線

		Return context manager to caller which need to make sure connection is closed after RPC invokes

		Return:
			這個物件的 Content Manager / Context manager of this instance
		"""
		return closing(self)

	def _update_location_set(self, location_set):
		self.location_set = location_set

	def _invoke_ignoreexcept(self, method_name, *args, **kwds):
		if self._client is not None:
			try:
				return _invoke(self._client, method_name, args, kwds)
			except Exception:
				_log.exception("failed on invoke [%r] on cached client (%r)", method_name, self.location_set)
		self.close()
		for host, port in self.location_set:
			try:
				self._client, self._transport, = _connect(self.client_cls, host, port, self._timeout)
				return _invoke(self._client, method_name, args, kwds)
			except Exception:
				_log.exception("failed on invoke [%r] on [%r:%r]", method_name, host, port)
			self.close()
		raise OutOfLocationSet(method_name)

	def _invoke_except(self, method_name, exp_no_ignore, *args, **kwds):
		if self._client is not None:
			try:
				return _invoke(self._client, method_name, args, kwds)
			except Exception as e:
				if isinstance(e, exp_no_ignore):
					raise
				_log.exception("failed on invoke [%r] on cached client (%r)", method_name, self.location_set)
		self.close()
		for host, port in self.location_set:
			try:
				self._client, self._transport, = _connect(self.client_cls, host, port, self._timeout)
				return _invoke(self._client, method_name, args, kwds)
			except Exception as e:
				if isinstance(e, exp_no_ignore):
					raise
				_log.exception("failed on invoke [%r] on [%r:%r]", method_name, host, port)
			self.close()
		raise OutOfLocationSet(method_name)

	def close(self):
		# type: () -> None
		try:
			self._transport.close()
		except Exception:
			pass
		self._client = None
		self._transport = None

	def acquire_client_lock(self):
		# type: () -> None
		self._lockobject.acquire()

	def release_client_lock(self):
		# type: () -> None
		self._lockobject.release()

	def __enter__(self):
		self._lockobject.acquire()
		return self

	def __exit__(self, ex_type, ex_value, ex_traceback):
		self._lockobject.release()

	# pylint: disable=function-redefined
	def __getattr__(self, name):
		if name in self._cached_invoker:
			f = self._cached_invoker[name]
			return f
		# {{{ setup proxy callable
		if self._passthrough_exception:
			# with exceptions to ignore
			def f(*args, **kwds):
				return self._invoke_except(name, self._passthrough_exception, *args, **kwds)
		else:
			# without exceptions to ignore
			def f(*args, **kwds):
				return self._invoke_ignoreexcept(name, *args, **kwds)

		# }}} setup proxy callable
		self._cached_invoker[name] = f
		return f


# vim: ts=4 sw=4 ai nowrap
