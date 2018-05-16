# -*- coding: utf-8 -*-
""" WebSocket 支援函式 / WebSocket support routines """

import socket
import struct
import time
import thread
import logging

_log = logging.getLogger(__name__)


class ResponseTooLarge(Exception):
	def __init__(self, size, limit):
		super(ResponseTooLarge, self).__init__("response too large: %r (limit=%r)" % (size, limit))


class ProtocolSwitchFailed(Exception):
	def __init__(self, response_line):
		super(ProtocolSwitchFailed, self).__init__("failed on switch protocol: " + response_line)


# pylint: disable=too-many-arguments
def _setup_websocket_connection_impl_send_request(fp, host, port, http_method, http_path, http_headers):
	fp.write(http_method + " " + http_path + " " + "HTTP/1.1\r\n")
	for k, v in http_headers.iteritems():
		if k == "Host":
			fp.write("Host: " + host + ":" + str(port) + "\r\n")
		elif k == "Origin":
			fp.write("Origin: http://" + host + ":" + str(port) + "\r\n")
		else:
			fp.write(k + ": " + v + "\r\n")
	fp.write("\r\n")
	fp.flush()
	respline = fp.readline(65537)
	if len(respline) > 65536:
		raise ResponseTooLarge(len(respline), 65536)
	respline = respline.strip("\r\n")
	aux = respline.split()
	if (len(aux) < 3) or (aux[1] != "101"):
		raise ProtocolSwitchFailed(respline)
	return respline


def _setup_websocket_connection_impl_fetch_headers(fp):
	result = {}
	l = fp.readline(65537)
	while l:
		l = l.rstrip("\r\n")
		if not l:
			break
		aux = l.split(":", 1)
		if len(aux) != 2:
			_log.warning("cannot split header entry: %r", l)
		k = aux[0]
		v = aux[1].lstrip()
		result[k] = v
		l = fp.readline(65537)
	return result


# pylint: disable=too-many-arguments
def setup_websocket_connection(host, port, http_method, http_path, http_headers, timeout=10.0):
	"""
	建立 WebSocket 連線

	Start a WebSocket connection

	Args:
		host: 連線目標的主機位址 / Host address of connection target
		port: 連線目標的 TCP 通訊埠 / TCP port number of connection target
		http_method: 建立 HTTP 連線時要使用的 HTTP 方法 / HTTP method for starting HTTP transcation
		http_path: 建立 HTTP 連線時要使用的資源路徑 / Resource path for starting HTTP transcation
		http_headers: 建立 HTTP 連線時要使用的 HTTP 標頭 / HTTP headers for starting HTTP transcation
		timeout=10.0: 逾時秒數 / Seconds for timeout

	Return:
		傳回一 (socket_object, socket_file, response_line, headers) 型式的 tuple 物件，分別代表: 連線的 Socket 物件、包裝前項 Socket 物件的檔案物件、遠
		端主機所回應的狀態行、遠端主機所回應的 HTTP 標頭字典

		Returns a tuple in (socket_object, socket_file, response_line, headers) form. The elements in resulted tuple represents: Socket object for connection,
		File object of socket, Status line from remote server, HTTP headers from remote server in dict object
	"""
	s = socket.create_connection((host, port), timeout)
	s.settimeout(None)
	try:
		f = s.makefile()
		respline = _setup_websocket_connection_impl_send_request(f, host, port, http_method, http_path, http_headers)
		h = _setup_websocket_connection_impl_fetch_headers(f)
	except Exception as e:
		_log.exception("failed on making websocket connection")
		try:
			f.close()
		except Exception:
			pass
		try:
			s.close()
		except Exception:
			pass
		raise e
	return (s, f, respline, h)


DF_HEADER = struct.Struct(">BB")
DF_LEN16 = struct.Struct(">H")
DF_LEN64 = struct.Struct(">Q")
DF_MASKEY = struct.Struct(">L")


class _WebSocketForwarder(object):
	def __init__(self, i_fp, o_fp, link_id=None, *args, **kwds):
		super(_WebSocketForwarder, self).__init__(*args, **kwds)
		self.i_fp = i_fp
		self.o_fp = o_fp
		self.link_id = link_id
		self.close_lock = thread.allocate_lock()

	def fetch_frame(self):
		b1 = self.i_fp.read(2)
		v0, v1 = DF_HEADER.unpack(b1)
		opcode = v0 & 0x0F
		has_mask = True if ((v1 & 0x80) != 0) else False
		payload_len = v1 & 0x7F
		if payload_len < 126:
			b2 = None
			b3 = None
		elif payload_len == 126:
			b2 = self.i_fp.read(2)
			payload_len, = DF_LEN16.unpack(b2)
			b3 = None
		else:
			b2 = None
			b3 = self.i_fp.read(8)
			payload_len, = DF_LEN64.unpack(b3)
		if has_mask:
			b4 = self.i_fp.read(4)
		else:
			b4 = None
		if payload_len > 0:
			b5 = self.i_fp.read(payload_len)
		else:
			b5 = None
		frame_blocks = (b1, b2, b3, b4, b5)
		return (opcode, payload_len, frame_blocks)

	def write_frame(self, frame_blocks):
		for b in frame_blocks:
			if b is None:
				continue
			self.o_fp.write(b)
		self.o_fp.flush()

	def _loop(self):
		opcode = 0
		while opcode != 0x8:
			opcode, payload_len, frame_blocks = self.fetch_frame()
			_log.debug("%r: data frame: opcode=0x%X, payload-length=%r", self, opcode, payload_len)
			self.write_frame(frame_blocks)

	def run(self, start_lock):
		with self.close_lock:
			start_lock.release()
			start_lock = None
			self._loop()

	def forwarding(self):
		return self.close_lock.locked()

	def __repr__(self):
		return "_WebSocketForwarder(%r, forwarding=%r)" % (self.link_id, self.forwarding())


def _forward_connection_impl_make_forwarder(src_i_fp, src_o_fp, dst_i_fp, dst_o_fp, link_id):
	src_dst_fwdr = _WebSocketForwarder(src_i_fp, dst_o_fp, link_id + ":(->)")
	dst_src_fwdr = _WebSocketForwarder(dst_i_fp, src_o_fp, link_id + ":(<-)")
	start_lock = thread.allocate_lock()
	start_lock.acquire()
	thread.start_new_thread(src_dst_fwdr.run, (start_lock, ))
	start_lock.acquire()
	thread.start_new_thread(dst_src_fwdr.run, (start_lock, ))
	with start_lock:
		start_lock = None
	return (src_dst_fwdr, dst_src_fwdr)


def _forward_connection_impl_wait_stop(src_dst_fwdr, dst_src_fwdr):
	stop_countdown = 10
	while (src_dst_fwdr.forwarding() or dst_src_fwdr.forwarding()) and (stop_countdown > 0):
		_log.debug("waiting for forwarder stop: %r, %r", src_dst_fwdr, dst_src_fwdr)
		time.sleep(2)
		stop_countdown = stop_countdown - 1
	if src_dst_fwdr.forwarding():
		_log.warning("forwarder still working even peer stopped: %r", src_dst_fwdr)
	if dst_src_fwdr.forwarding():
		_log.warning("forwarder still working even peer stopped: %r", dst_src_fwdr)


def forward_connection(src_i_fp, src_o_fp, dst_i_fp, dst_o_fp, link_id=None):
	"""
	在兩組 socket 之間轉送 WebSocket 資料塊，轉送邏輯會開啟分離的 thread 來進行
	資料塊的讀取與寫入，並僅在轉送了 close control frame (opcode = 0x08) 或是連
	線中斷之後才會停止轉送。

	Forward WebSocket data frames between two pair of sockets. The forwarding
	operation will conduct in seperated thread. The forwarding thread will stop
	after forwarded close control frame or failed link.

	Args:
		src_i_fp, src_o_fp: 要轉送的第一組 socket 的讀寫用 File Object / File objects of 1st pair of sockets
		dst_i_fp, dst_o_fp: 要轉送的第二組 socket 的讀寫用 File Object / File objects of 2nd pair of sockets
		link_id=None: 轉送識別代碼，偵錯訊息使用 / Forwarding link identifier
	"""
	if link_id is None:
		link_id = "forward_connection(%r, %r, %r, %r)" % (src_i_fp, src_o_fp, dst_i_fp, dst_o_fp)
	src_dst_fwdr, dst_src_fwdr = _forward_connection_impl_make_forwarder(src_i_fp, src_o_fp, dst_i_fp, dst_o_fp, link_id)
	while src_dst_fwdr.forwarding() and dst_src_fwdr.forwarding():
		_log.debug("forwarder is working: %r, %r", src_dst_fwdr, dst_src_fwdr)
		time.sleep(10)
	_forward_connection_impl_wait_stop(src_dst_fwdr, dst_src_fwdr)
