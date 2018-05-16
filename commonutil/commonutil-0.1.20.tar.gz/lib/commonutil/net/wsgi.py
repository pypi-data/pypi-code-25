# -*- coding: utf-8 -*-
""" WSGI 支援函式 / WSGI support routines """

import re
import time
import datetime
from contextlib import closing as context_closing
from string import whitespace
from os import stat as path_stat
from os.path import abspath
from os.path import normpath
from os.path import isfile
from os.path import join as joinpath
from mimetypes import guess_type as mime_guess_type
from json import dumps as json_dumps
from hashlib import sha256
from httplib import HTTPConnection, HTTPSConnection
from wsgiref.handlers import SimpleHandler
from wsgiref.simple_server import WSGIRequestHandler as SimpleWSGIRequestHandler
from wsgiref.util import is_hop_by_hop
from zipfile import ZipFile
import logging

from commonutil.net import websocket

_log = logging.getLogger(__name__)

_PATH_STRIP_CHARACTERS = "/" + whitespace

_TEXT_WEEKDAY = (
		"Mon",
		"Tue",
		"Wed",
		"Thu",
		"Fri",
		"Sat",
		"Sun",
)
_TEXT_MONTH = (
		"Jan",
		"Feb",
		"Mar",
		"Apr",
		"May",
		"Jun",
		"Jul",
		"Aug",
		"Sep",
		"Oct",
		"Nov",
		"Dec",
)


def httpdate_from_datetime(dt):
	# type: (datetime.datetime) -> str
	"""
	傳回給定 datetime.datetime 物件的 RFC 7231 (HTTP/1.1) 字串，給定的物件必須在 UTC 時區。

	Return a string representation of given datetime.datetime object according to RFC 1123 (HTTP/1.1).
	The supplied datetime object must be in UTC.

	Args:
		dt: 要輸出的時間之 datetime.datetime 物件 / datetime.datetime object of required date

	Return:
		HTTP 時間字串 / HTTP date string
	"""
	return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
			_TEXT_WEEKDAY[dt.weekday()],
			dt.day,
			_TEXT_MONTH[dt.month - 1],
			dt.year,
			dt.hour,
			dt.minute,
			dt.second,
	)


def httpdate_from_timestamp(tstamp):
	# type: (int) -> str
	"""
	傳回給定 EPOCH 時戳的 RFC 7231 (HTTP/1.1) 字串。

	Return a string representation of given epoch time-stamp according to RFC 1123 (HTTP/1.1).

	Args:
		dt: 要輸出的時間之時戳 / time-stamp of required date

	Return:
		HTTP 時間字串 / HTTP date string
	"""
	dt = datetime.datetime.utcfromtimestamp(tstamp)
	return httpdate_from_datetime(dt)


_MONTH_KEYMAP = {
		"JAN": 1,
		"FEB": 2,
		"MAR": 3,
		"APR": 4,
		"MAY": 5,
		"JUN": 6,
		"JUL": 7,
		"AUG": 8,
		"SEP": 9,
		"OCT": 10,
		"NOV": 11,
		"DEC": 12,
}

_HTTPDATE_REGEX = re.compile(r"[A-Za-z]+,\s*([0-9]+)\s+([A-Za-z]+)\s+([0-9]+)\s+([0-9]+):([0-9]+):([0-9]+)\s+(GMT|UTC)")


def parse_httpdate(v):
	# type: (str) -> Optional[datetime.datetime]
	"""
	解析 HTTP 時間字串，傳回 datetime.datetime 物件

	Parse HTTP date string into datetime.datetime object

	Args:
		v: 要解析的字串 / String to parse

	Return:
		解析成功的 datetime.datetime 物件，或是 None / Return datetime.datetime object when parsing success, None otherwise.
	"""
	m = _HTTPDATE_REGEX.match(v)
	if m:
		try:
			day = int(m.group(1))
			month = _MONTH_KEYMAP[m.group(2).upper()]
			year = int(m.group(3))
			hour = int(m.group(4))
			minute = int(m.group(5))
			second = int(m.group(6))
			return datetime.datetime(year, month, day, hour, minute, second)
		except Exception:
			_log.exception("failed on parsing HTTP date text: %r", v)
	return None


HEADER_NO_CACHE = [
		("Cache-Control", "no-cache, must-revalidate"),  # HTTP/1.1
		("Expires", "Mon, 26 Jul 1997 05:00:00 GMT"),
		("Pragma", "no-cache"),
]  # Pragma: no-cache - HTTP/1.0, for elder proxies

HEADAR_MIME_TEXT = [
		("Content-Type", "text/plain"),
]


def make_expire_header(expire_seconds=600):
	# type: (int) -> List[Tuple[str, str]]
	"""
	建立內容過期時間的標頭資訊。

	Make header list for content expiration.

	Args:
		expire_seconds=600: 標頭內標示資料過期的秒數 / Content expiration seconds

	Return:
		標頭串列物件 / List of header content
	"""
	expire_tstamp = int(time.time()) + expire_seconds
	return [
			("Cache-Control", "private"),
			("Expires", httpdate_from_timestamp(expire_tstamp)),
			("Pragma", "no-cache"),
	]  # Pragma: no-cache - HTTP/1.0, for elder proxies


def fill_text_response(start_response, http_status, message_text=None):
	# type: (Callable[..., None], str, Optional[str]) -> Iterator[str]
	"""
	傳回 HTTP 標頭與純文字內容。

	Return HTTP headers and plain text content body.

	Args:
		start_response: WSGI 回應函數物件 / WSGI response callable
		http_status: HTTP 狀態碼 / HTTP status code
		message_text=None: 要傳送的文字內容 / Text content to place into content body

	Yield:
		文字內容 / Text body
	"""
	start_response(http_status, HEADER_NO_CACHE + HEADAR_MIME_TEXT)
	if message_text:
		yield message_text


def fill_response_403(start_response, message_text="Forbidden"):
	# type: (Callable[..., None], Optional[str]) -> Iterator[str]
	"""
	傳回 HTTP 403 Forbidden 標頭與內容。

	Return HTTP 403 Forbidden headers and text content body.

	Args:
		start_response: WSGI 回應函數物件 / WSGI response callable
		message_text="Forbidden": 要傳送的文字內容 / Text content to place into content body

	Yield:
		文字內容 / Text body
	"""
	return fill_text_response(start_response, "403 Forbidden", message_text)


def fill_response_404(start_response, message_text="Not Found"):
	# type: (Callable[..., None], Optional[str]) -> Iterator[str]
	"""
	傳回 HTTP 404 Not Found 標頭與內容。

	Return HTTP 404 Not Found headers and text content body.

	Args:
		start_response: WSGI 回應函數物件 / WSGI response callable
		message_text="Not Found": 要傳送的文字內容 / Text content to place into content body

	Yield:
		文字內容 / Text body
	"""
	return fill_text_response(start_response, "404 Not Found", message_text)


def fill_response_500(start_response, message_text="Internal Server Error"):
	# type: (Callable[..., None], Optional[str]) -> Iterator[str]
	"""
	傳回 HTTP 500 Internal Server Error 標頭與內容。

	Return HTTP 500 Internal Server Error headers and text content body.

	Args:
		start_response: WSGI 回應函數物件 / WSGI response callable
		message_text="Internal Server Error": 要傳送的文字內容 / Text content to place into content body

	Yield:
		文字內容 / Text body
	"""
	return fill_text_response(start_response, "500 Internal Server Error", message_text)


def fill_response_501(start_response, message_text="Not Implemented"):
	# type: (Callable[..., None], Optional[str]) -> Iterator[str]
	"""
	傳回 HTTP 501 Not Implemented 標頭與內容。

	Return HTTP 501 Not Implemented headers and text content body.

	Args:
		start_response: WSGI 回應函數物件 / WSGI response callable
		message_text="Not Implemented": 要傳送的文字內容 / Text content to place into content body

	Yield:
		文字內容 / Text body
	"""
	return fill_text_response(start_response, "501 Not Implemented", message_text)


def fill_response_503(start_response, message_text="Service Unavailable"):
	# type: (Callable[..., None], Optional[str]) -> Iterator[str]
	"""
	傳回 HTTP 503 Service Unavailable 標頭與內容。

	Return HTTP 503 Service Unavailable headers and text content body.

	Args:
		start_response: WSGI 回應函數物件 / WSGI response callable
		message_text="Service Unavailable": 要傳送的文字內容 / Text content to place into content body

	Yield:
		文字內容 / Text body
	"""
	return fill_text_response(start_response, "503 Service Unavailable", message_text)


def fill_response_304(start_response, etag, last_modify, expire_seconds=600, message_text="Not Modified"):
	# type: (Callable[..., None], str, datetime.datetime, int, int, Optional[str]) -> Iterator[str]
	"""
	傳回 HTTP 304 Not Modified 標頭與內容。

	Return HTTP 304 Not Modified headers and text content body.

	Args:
		start_response: WSGI 回應函數物件 / WSGI response callable
		etag: HTTP ETag 標頭內容 / Header content of HTTP ETag
		last_modify: HTTP Last-Modified 最後更新時間標頭字串 / Header content of HTTP Last-Modified
		expire_seconds=600: 標頭內標示資料過期的秒數 / Content expiration seconds
		message_text="Not Modified": 要傳送的文字內容 / Text content to place into content body

	Yield:
		文字內容 / Text body
	"""
	start_response("304 Not Modified",
					make_expire_header(expire_seconds) + [
							("ETag", etag),
							("Last-Modified", last_modify),
					])
	if message_text:
		yield message_text


_EPOCH_DATETIME = datetime.datetime.utcfromtimestamp(0)


# pylint: disable=too-many-arguments
def _do_conditional_get(environ, start_response, etag, last_modify, modify_timestamp, acceptable_aging_sec=1):
	""" (internal) Perform conditional-get

	Return:
		Return output generator on conditional get.
		Return None when not conditional get operation.
	"""
	remote_etag = environ.get("HTTP_IF_NONE_MATCH", "")
	if remote_etag == etag:
		return fill_response_304(start_response, etag, last_modify)
	remote_last_modify = environ.get("HTTP_IF_MODIFIED_SINCE", "")
	if remote_last_modify == last_modify:
		return fill_response_304(start_response, etag, last_modify)
	if remote_last_modify:
		aux = parse_httpdate(remote_last_modify)
		if (aux is not None) and ((modify_timestamp - (aux - _EPOCH_DATETIME).total_seconds()) < acceptable_aging_sec):
			return fill_response_304(start_response, etag, last_modify)
	return None


def _filter_response_header(headers):
	result = []
	for n, v in headers:
		if is_hop_by_hop(n):
			_log.debug("stripped hop-by-hop header: %r => %r", n, v)
		else:
			result.append((n, v))
	return result


# pylint: disable=too-many-arguments, unused-argument
def fill_json_response(environ, start_response, data_content, modify_timestamp, acceptable_aging_seconds=3, expire_seconds=600, json_indent=None):
	# type: (Dict[str, str], Callable[..., None], Any, datetime.datetime, int, int, Optional[str]) -> Iterator[str]
	"""
	傳回給定基本資料物件的 JSON 型式輸出的標頭與內容

	Output JSON form of given primitive data construct.

	Args:
		environ, start_response: WSGI 參數 / WSGI parameters
		data_content: 要轉換成 JSON 的基本資料物件 / Data construct to export as JSON
		modify_timestamp: 用在 HTTP Last-Modified 最後更新時間標頭字串的時戳 / Time-stamp for header content of HTTP Last-Modified
		acceptable_aging_seconds=3: 當遠端資料舊於給定秒數時不更新，如給定 None 時不進行 conditional-request 檢查 / Do not perform update when client content is aging with-in given seconds. Skip conditional-request test if None is given.
		expire_seconds=600: 標頭內標示資料過期的秒數 / Content expiration seconds
		json_indent=None: 是否要縮排 JSON 輸出 / Indent JSON output
	"""
	json_opts = {}
	if json_indent:
		json_opts["indent"] = json_indent
	result = json_dumps(data_content, **json_opts)
	digest = sha256(result).hexdigest()
	last_modify = httpdate_from_timestamp(modify_timestamp)
	etag = "\"" + digest + "\""
	# {{{ conditional get
	if acceptable_aging_seconds is not None:
		aux = _do_conditional_get(environ, start_response, etag, last_modify, modify_timestamp, acceptable_aging_seconds)
		if aux:
			return aux
	# }}} conditional get
	start_response("200 OK",
					make_expire_header() + [
							("ETag", etag),
							("Last-Modified", last_modify),
							("Content-Type", "application/json"),
							("Content-Length", str(len(result))),
					])
	return (result, )


_HEADER_UPPER_WORD = frozenset((
		"TE",
		"DNT",
		"ATT",
		"UIDH",
		"ID",
		"P3P",
		"MD5",
		"WWW",
		"XSS",
		"CSP",
		"UA",
))
_HEADER_MIXCAP_WORD = {
		"ETAG": "ETag",
		"WEBSOCKET": "WebSocket",
}


def _header_word_mapping(v):
	if v in _HEADER_MIXCAP_WORD:
		return _HEADER_MIXCAP_WORD[v]
	elif v in _HEADER_UPPER_WORD:
		return v
	return v.capitalize()


def extract_headers(environ):
	# type: (Dict[str, str]) -> Dict[str, str]
	"""
	從給定的環境變數字典中取出 HTTP 標頭

	Extract HTTP header from given environment variable dictionary

	Args:
		environ: PEP-333 中定義的環境變數字典 / Environment variable dictionary defined in PEP-333

	Return:
		含有 HTTP header 的字典 / Dictionary contains HTTP header
	"""
	result = {}
	for h_key, h_value, in environ.iteritems():
		h_key = h_key.upper()
		if h_key == "CONTENT_TYPE":
			r_key = "Content-Type"
		elif h_key == "CONTENT_LENGTH":
			if not h_value:
				continue
			r_key = "Content-Length"
		elif h_key[:5] == "HTTP_":
			aux = map(_header_word_mapping, h_key[5:].split("_"))
			r_key = "-".join(aux)
		else:
			continue
		result[r_key] = h_value
	return result


def get_request_body(environ, default_content=""):
	# type: (Dict[str, str], str) -> str
	"""
	取出使用者端傳送的 HTTP request 的內容本體

	Fetch HTTP request body from client

	Args:
		environ: PEP-333 中定義的環境變數字典 / Environment variable dictionary defined in PEP-333

	Return:
		使用者端傳送的 HTTP request 內容本體 / Request body from client
	"""
	try:
		l = environ.get("CONTENT_LENGTH")
		l = int(l) if l else 0
	except Exception:
		l = 0
	if l > 0:
		request_body = environ["wsgi.input"].read(l)
		return request_body
	return default_content


class StaticFileHandler(object):
	"""
	提供靜態檔案的 WSGI handler

	WSGI handler offers static file serving
	"""

	def __init__(self, root_path, *args, **kwds):
		# type: (str) -> None
		""" (建構子 / Constructor)

		Args:
			root_path: 檔案資料夾的路徑，必須為絕對路徑 / Absolute path to file folder
		"""
		super(StaticFileHandler, self).__init__(*args, **kwds)
		self._root_path = root_path

	def __call__(self, environ, start_response, shifted_url_path=None):
		"""
		處理函數，當檔案路徑未給定時會由 PATH_INFO 環境變數中抓取。
		呼叫的函數可利用 `wsgiref.util.shift_path_info(environ)` 或是類似的函數預先調整 PATH_INFO 環境變數的內容。

		Handling callable. Will get file path from PATH_INFO environment variable.
		Caller can adjust content of PATH_INFO by `wsgiref.util.shift_path_info(environ)` or similar functions.

		Args:
			environ, start_response: WSGI 參數 / WSGI parameters
			shifted_url_path=None: 目標的檔案 URL 路徑 / URL path to target file
		"""
		if not shifted_url_path:
			shifted_url_path = environ.get("PATH_INFO", "")
		shifted_url_path = shifted_url_path.lstrip(_PATH_STRIP_CHARACTERS)
		file_path = abspath(joinpath(self._root_path, shifted_url_path))
		if not file_path.startswith(self._root_path):
			return fill_response_403(start_response)
		if not isfile(file_path):
			return fill_response_404(start_response)
		file_stat = path_stat(file_path)
		mtime = int(file_stat.st_mtime)
		last_modify = httpdate_from_timestamp(mtime)
		etag = "\"" + str(mtime) + "\""
		# {{{ conditional get
		aux = _do_conditional_get(environ, start_response, etag, last_modify, mtime)
		if aux:
			return aux
		# }}} conditional get
		mime_type, _content_encoding, = mime_guess_type(file_path)
		if not mime_type:
			mime_type = "application/octet-stream"
		start_response("200 OK",
						make_expire_header() + [
								("ETag", etag),
								("Last-Modified", last_modify),
								("Content-Type", mime_type),
								("Content-Length", str(file_stat.st_size)),
						])
		file_wrapper = environ.get("wsgi.file_wrapper")
		fp = open(file_path, "rb")
		if file_wrapper:
			return file_wrapper(fp, 4096)
		return iter(lambda: fp.read(4096), "")

	def __repr__(self, *_args, **_kwds):
		return "%s.StaticFileHandler(root_path=%r)" % (
				__name__,
				self._root_path,
		)


class StaticZipFileHandler(object):
	"""
	提供以 Zip 檔案內容作為靜態檔案的 WSGI handler

	WSGI handler offers static file serving from zip file
	"""

	def __init__(self, zip_file_path, prefix_folder=None, *args, **kwds):
		# type: (str, Optional[str]) -> None
		""" (建構子 / Constructor)

		Args:
			zip_file_path: 存放檔案內容的 Zip 檔案路徑 / Absolute path to zip file
			path_prefix: 檔案資料夾的路徑，必須為絕對路徑 / Absolute path to file folder
		"""
		super(StaticZipFileHandler, self).__init__(*args, **kwds)
		self._zip_file_path = zip_file_path
		self._prefix_folder = None if (not prefix_folder) else prefix_folder.strip(_PATH_STRIP_CHARACTERS)

	# pylint: disable=too-many-locals
	def __call__(self, environ, start_response, shifted_url_path=None):
		"""
		處理函數，當檔案路徑未給定時會由 PATH_INFO 環境變數中抓取。
		呼叫的函數可利用 `wsgiref.util.shift_path_info(environ)` 或是類似的函數預先調整 PATH_INFO 環境變數的內容。

		Handling callable. Will get file path from PATH_INFO environment variable.
		Caller can adjust content of PATH_INFO by `wsgiref.util.shift_path_info(environ)` or similar functions.

		Args:
			environ, start_response: WSGI 參數 / WSGI parameters
			shifted_url_path=None: 目標的檔案 URL 路徑 / URL path to target file
		"""
		if not shifted_url_path:
			shifted_url_path = environ.get("PATH_INFO", "")
		shifted_url_path = shifted_url_path.lstrip(_PATH_STRIP_CHARACTERS)
		if self._prefix_folder is None:
			file_path = normpath(shifted_url_path)
			l = len(file_path)
			# pylint: disable=too-many-boolean-expressions
			if ((l == 1) and (file_path in (
					".",
					"/",
			))) or ((l >= 2) and (file_path[:2] == "./")) or ((l >= 2) and (file_path[:3] == "../")):
				file_path = None
		else:
			file_path = normpath("/".join((
					self._prefix_folder,
					shifted_url_path,
			)))
			if not file_path.startswith(self._prefix_folder):
				file_path = None
		if not file_path:
			return fill_response_403(start_response)
		with ZipFile(self._zip_file_path, "r") as zipfp:
			try:
				file_info = zipfp.getinfo(file_path)
			except KeyError:
				return fill_response_404(start_response)
			m_dt = datetime.datetime(*file_info.date_time)
			mtime = (m_dt - _EPOCH_DATETIME).total_seconds()
			last_modify = httpdate_from_datetime(m_dt)
			etag = "\"" + str(mtime) + "\""
			# {{{ conditional get
			aux = _do_conditional_get(environ, start_response, etag, last_modify, mtime)
			if aux:
				return aux
			# }}} conditional get
			mime_type, _content_encoding, = mime_guess_type(file_path)
			if not mime_type:
				mime_type = "application/octet-stream"
			file_size = file_info.file_size
			start_response("200 OK",
							make_expire_header() + [
									("ETag", etag),
									("Last-Modified", last_modify),
									("Content-Type", mime_type),
									("Content-Length", str(file_size)),
							])
			fp = zipfp.open(file_info, "r")
			content_blob = fp.read()
		return (content_blob, )

	def __repr__(self, *_args, **_kwds):
		return "%s.StaticZipFileHandler(zip_file_path=%r, prefix_folder=%r)" % (
				__name__,
				self._zip_file_path,
				self._prefix_folder,
		)


class ForwardingHandler(object):
	"""
	提供轉送查詢的 WSGI handler

	WSGI handler forwarding request to other HTTP service
	"""

	def __init__(self, base_path, https_server, host, port, *connection_args, **connection_kwds):
		# type: (str, bool, *Any, **Any) -> None
		""" (建構子 / Constructor)

		Args:
			base_path: 基底網址路徑部份 / URL to proxy target
			https_server: 遠端是否為 HTTPS 服務 / Is remote server running HTTPS service
			*connection_args, **connection_kwds: 要傳遞給 HTTPConnection 或 HTTPSConnection 的參數 / Parameters for HTTPConnection or HTTPSConnection connection
		"""
		super(ForwardingHandler, self).__init__()
		self._base_path = "/" + base_path.strip(_PATH_STRIP_CHARACTERS) + "/"
		if self._base_path == "//":
			self._base_path = "/"
		self._connection_cls = HTTPSConnection if https_server else HTTPConnection
		self._conn_host = host
		self._conn_port = port
		self._connection_args = connection_args
		self._connection_kwds = connection_kwds
		self._http_request_debuglevel = 0

	def set_debuglevel(self, level):
		# type: (int) -> None
		self._http_request_debuglevel = level

	# pylint: disable=too-many-locals
	def forward_websocket(self, environ, start_response, shifted_url_path, http_method, proxied_path, proxied_headers):
		if ("wsgix.output" not in environ) or ("wsgix.fence" not in environ):
			_log.warning(
					"cannot handle websocket upgrade: require wsgix.output and wsgix.fence attribute from ExtendedWSGIRequestHandler or compatible handler")
			return False
		dst_o_fp = environ["wsgix.output"]
		dst_i_fp = environ["wsgi.input"]
		environ["wsgix.fence"]()
		ws_sp, src_fp, respline, headers = websocket.setup_websocket_connection(self._conn_host, self._conn_port, http_method, proxied_path, proxied_headers)
		with context_closing(ws_sp), context_closing(src_fp):
			dst_o_fp.write(respline + "\r\n")
			for k, v in headers.iteritems():
				dst_o_fp.write(k + ": " + v + "\r\n")
			dst_o_fp.write("\r\n")
			dst_o_fp.flush()
			websocket.forward_connection(src_fp, src_fp, dst_i_fp, dst_o_fp, proxied_path)
		return True

	def handle_connection_switch(self, environ, start_response, shifted_url_path, http_method, proxied_path, proxied_headers):
		hdr_conn = tuple(reversed(map(lambda x: x.strip().upper(), proxied_headers.get("Connection", "").split(","))))
		if "UPGRADE" in hdr_conn:  # able to handle UPGRADE only
			upgrade_type = proxied_headers.get("Upgrade", "").upper()
			if upgrade_type == "WEBSOCKET":
				return self.forward_websocket(environ, start_response, shifted_url_path, http_method, proxied_path, proxied_headers)
			_log.warning("cannot handle requested connection upgrade: %r", upgrade_type)
		return False

	# pylint: disable=too-many-locals
	def __call__(self, environ, start_response, shifted_url_path=None):
		"""
		處理函數，當相對路徑未給定時會由 PATH_INFO 環境變數中抓取。
		呼叫的函數可利用 `wsgiref.util.shift_path_info(environ)` 或是類似的函數預先調整 PATH_INFO 環境變數的內容。

		Handling callable. Will get relative URL path from PATH_INFO environment variable.
		Caller can adjust content of PATH_INFO by `wsgiref.util.shift_path_info(environ)` or similar functions.

		Args:
			environ, start_response: WSGI 參數 / WSGI parameters
			shifted_url_path=None: 目標的檔案 URL 路徑 / URL path to target file
		"""
		if not shifted_url_path:
			shifted_url_path = environ.get("PATH_INFO", "")
		shifted_url_path = shifted_url_path.lstrip(_PATH_STRIP_CHARACTERS)
		http_method = environ.get("REQUEST_METHOD", "").upper()
		query_string = environ.get("QUERY_STRING")
		if query_string:
			proxied_path = self._base_path + shifted_url_path + "?" + query_string
		else:
			proxied_path = self._base_path + shifted_url_path
		proxied_headers = extract_headers(environ)
		if self.handle_connection_switch(environ, start_response, shifted_url_path, http_method, proxied_path, proxied_headers):
			start_response("101 Switched", HEADER_NO_CACHE + HEADAR_MIME_TEXT)
			yield "Switched"
			return
		request_body = get_request_body(environ, None)
		conn = self._connection_cls(self._conn_host, self._conn_port, *self._connection_args, **self._connection_kwds)
		try:
			if self._http_request_debuglevel:
				conn.set_debuglevel(self._http_request_debuglevel)
			conn.request(http_method, proxied_path, request_body, proxied_headers)
			response = conn.getresponse()
			response_code = str(response.status) + " " + str(response.reason)
			response_headers = _filter_response_header(response.getheaders())
			start_response(response_code, response_headers)
			while response is not None:
				d = response.read(4096)
				if d:
					yield d
				else:
					response = None
			caught_exception = None
		except Exception as e:
			_log.exception("failed on forwarding response content")
			caught_exception = e
		finally:
			conn.close()
		if caught_exception:
			raise caught_exception  # pylint: disable=raising-bad-type

	def __repr__(self, *_args, **_kwds):
		return "%s.ForwardingHandler(base_path=%r, connection_cls=%r, connection_host=%r, connection_port=%r, *connection_args=%r, **connection_kwds=%r)" % (
				__name__,
				self._base_path,
				self._connection_cls,
				self._conn_host,
				self._conn_port,
				self._connection_args,
				self._connection_kwds,
		)


class _ExtSimpleHandler(SimpleHandler):
	def __init__(self, stdin, stdout, *args, **kwds):
		SimpleHandler.__init__(self, stdin, stdout, *args, **kwds)
		self._oninit_stdout = stdout
		self._unfensed_write = None
		self._unfensed_flush = None

	def _fenced_write(self, data):
		pass

	def _fenced_flush(self):
		self._write = self._unfensed_write
		self._flush = self._unfensed_flush
		self._flush()

	def fence(self):
		self._unfensed_write = self._write
		self._unfensed_flush = self._flush
		self._write = self._fenced_write
		self._flush = self._fenced_flush

	def setup_environ(self):
		SimpleHandler.setup_environ(self)
		self.environ['wsgix.output'] = self._oninit_stdout
		self.environ['wsgix.fence'] = self.fence

	def close(self):
		try:
			self.request_handler.log_request(self.status.split(' ', 1)[0], self.bytes_sent)
		finally:
			SimpleHandler.close(self)


class ExtendedWSGIRequestHandler(SimpleWSGIRequestHandler):
	def _error_request_too_large(self):
		self.requestline = ''
		self.request_version = ''
		self.command = ''
		self.send_error(414)

	def handle(self):
		"""Handle a single HTTP request"""
		self.raw_requestline = self.rfile.readline(65537)
		if len(self.raw_requestline) > 65536:
			self._error_request_too_large()
			return
		if not self.parse_request():  # An error code has been sent, just exit
			return
		handler = _ExtSimpleHandler(self.rfile, self.wfile, self.get_stderr(), self.get_environ())
		handler.request_handler = self
		handler.run(self.server.get_app())


# vim: ts=4 sw=4 ai nowrap
