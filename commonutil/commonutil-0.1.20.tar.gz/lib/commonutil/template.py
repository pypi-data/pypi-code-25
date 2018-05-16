# -*- coding: utf-8 -*-
""" 樣板檔案處理 / Template file processing """

from os.path import exists as is_path_exists
from hashlib import sha256

import logging
_log = logging.getLogger(__name__)

# macro: 值的操作或替代的相關元素
# context: 含有巨集標記的內容物件，內容物為已進行過內容替代
# template: 含有巨集標記的內容物件，內容物還沒有進行過內容替代
# content: 要被替代入檔案或內容物件中的巨集輸入


class BaseLineBlockedMacroMarker(object):
	""" 多行構成的塊狀資料樣板標記 / Line-blocked data template macro marker """

	def is_trapped_start_line(self, l):
		# type: (str) -> Optional[Tuple[str, str, Any]]
		""" 是否偵測到給定的資料列為巨集放置點的開始行

		Check if given content line is start line of content block

		Args:
			l: 要檢查的資料

		Return:
			當為開始行時傳回 (indent_text, block_name, marker_parameter,) 形式的 tuple 物件。
			分別代表: 縮排的空白字元組成的字串、巨集放置點名稱、這個標記的額外的參數物件
			如果不是則傳回 None
		"""
		raise NotImplementedError("not implemented: is_trapped_start_line()")

	def is_trapped_end_line(self, l):
		# type: (str) -> Optional[Tuple[str, str]]
		""" 是否偵測到給定的資料列為巨集放置點的結束行

		Check if given content line is end line of content block

		Args:
			l: 要檢查的資料

		Return:
			當為結束行時傳回 (indent_text, block_name,) 形式的 tuple 物件。
			分別代表: 縮排的空白字元組成的字串、巨集放置點名稱
			如果不是則傳回 None
		"""
		raise NotImplementedError("not implemented: is_trapped_end_line()")

	def wrap_line(self, l):  # pylint: disable=unused-argument
		# type: (str) -> str
		""" 針對給定的資料行進行再處理

		Perform extra actions on given line

		Args:
			l: 準備進行再處理的資料行

		Return:
			經過再處理的新資料行，或是 None 如果不需要再處理
		"""
		return None

	def get_one_line_marker(self, block_name, marker_parameter):
		# type: (str, Any) -> str
		""" 取得單行的巨集放置點標示

		Args:
			block_name: 巨集放置點的名字 / Name of given macro value block
			marker_parameter: 標記參數物件 / Parameter object of marker

		Return:
			表示單行的巨集放置點的字串
		"""
		raise NotImplementedError("not implemented: get_one_line_marker()")

	def get_block_line_markers(self, block_name, marker_parameter):
		# type: (str, Any) -> Tuple[str, str]
		""" 取得區塊用的巨集放置點標示

		Args:
			block_name: 巨集放置點的名字 / Name of given macro value block
			marker_parameter: 標記參數物件 / Parameter object of marker

		Return:
			一個 (tag_s, tag_e,) 形式的 tuple 物件，內容物件為資料區塊的巨集放置點的表示字串的起點與終點
		"""
		raise NotImplementedError("not implemented: get_block_line_markers()")


class BaseLineDigestMarker(object):
	""" 單行構成的資料樣板雜湊值標記 / Single-lined template digest marker """

	def is_trapped_digest_line(self, l):
		# type: (str) -> Optional[Tuple[str, str, Any]]
		""" 是否為可存有雜湊值的資料行

		Check if given content line is template digest line

		Args:
			l: 要檢查的資料

		Return:
			當為開始行時傳回 (indent_text, digest_code, marker_parameter,) 形式的 tuple 物件。
			分別代表: 縮排的空白字元組成的字串、雜湊碼、這個標記的額外的參數物件
			如果不是則傳回 None
		"""
		raise NotImplementedError("not implemented: is_trapped_hash_line()")

	def get_digest_line_marker(self, digest_code, marker_parameter):
		# type: (str, Any) -> str
		""" 取得雜湊值放置點標示

		Args:
			digest_code: 雜湊值 / Digest code of template
			marker_parameter: 標記參數物件 / Parameter object of marker

		Return:
			表示雜湊值的放置點字串
		"""
		raise NotImplementedError("not implemented: get_digest_line_marker()")


def _iter_context_line_innerloop(content, max_depth=8):
	# type: (Any, int) -> Generator[str]
	for l in content:
		if (max_depth > 0) and isinstance(l, (
				list,
				tuple,
				set,
		)):
			for ll in _iter_context_line_innerloop(l, max_depth - 1):
				yield ll
			yield None
		else:
			yield l


def _iter_context_line(content):
	# type: (Any) -> Generator[str]
	meet_none = False
	for l in _iter_context_line_innerloop(content):
		if l is None:
			meet_none = True
			continue
		if meet_none:
			meet_none = False
			yield None
		yield l


def _digest_context_line(content):
	# type: (Any) -> str
	digester = sha256()
	for l in _iter_context_line(content):
		if l is not None:
			digester.update(l)
		digester.update("\n")
	return digester.hexdigest().lower()


def _iter_digest_marked_context_line(content, digest_code, digest_marker):
	# type: (Any, str, BaseLineDigestMarker) -> Generator[str]
	for l in _iter_context_line(content):
		if l is not None:
			aux = digest_marker.is_trapped_digest_line(l)
			if aux is not None:
				indent_text, _digest_code, marker_parameter, = aux
				yield indent_text + digest_marker.get_digest_line_marker(digest_code, marker_parameter)
			else:
				yield l
		else:
			yield None


# pylint: disable=too-many-locals
def _render_flat_line_blocked_context(existed_line_iterator, content_map, marker, gap_line_for_block_marker=False, keep_empty_content_marker=True):
	# type: (Iterator[str], Dict[str, str], BaseLineBlockedMacroMarker, bool, bool) -> List[str]
	"""
	(internal) 將巨集值放入指定的樣板資料中，樣板資料為平坦無巢狀結構的資料串列

	Put macro values into given template content lines and return resulted lines. Given template must be flat string list.

	Args:
		existed_line_iterator: 要放入巨集值的樣板資料字串迭代器 / String iterator to place macro values into
		content_map: 巨集值的字典物件 / Dictionary contains macro values
		marker: 偵測巨集放置點的標記偵測與產生物件 / Marker detection and generation object
		gap_line_for_block_marker: 是否要在區塊標記與內容間放置一個空白行 / Place a blank line between placed content and block markers
		keep_empty_content_marker: 是否要保留沒有代換內容的標記 / Keep marker of empty content

	Return:
		儲存有已放入巨集資料的字串串列
	"""
	result_context = []
	in_content_block = False
	indent_text = ""
	block_name = None
	marker_parameter = None
	for l in existed_line_iterator:
		l = l.rstrip() if l else ""
		if not in_content_block:
			m = marker.is_trapped_start_line(l)
			if m is not None:
				indent_text, block_name, marker_parameter, = m
				in_content_block = True
		if in_content_block:
			m = marker.is_trapped_end_line(l)
			if m is not None:
				if (
						indent_text,
						block_name,
				) != m:
					_log.warning("unequal block marker parameter: %r, %r != %r", indent_text, block_name, m)
				in_content_block = False
				content = content_map.get(block_name)
				if content:
					tag_s, tag_e, = marker.get_block_line_markers(block_name, marker_parameter)
					result_context.append(indent_text + tag_s)
					if gap_line_for_block_marker:
						result_context.append("")
					for l in _iter_context_line(content):
						if l is None:
							result_context.append("")
						else:
							result_context.append(indent_text + l)
					if gap_line_for_block_marker:
						result_context.append("")
					result_context.append(indent_text + tag_e)
				elif keep_empty_content_marker:
					tag_one = marker.get_one_line_marker(block_name, marker_parameter)
					result_context.append(indent_text + tag_one)
				else:
					tag_one = marker.get_one_line_marker(block_name, marker_parameter)
					_log.info("marker w/o content: %r", tag_one)
			continue
		ll = marker.wrap_line(l)
		if ll is None:
			ll = l  # pylint: disable=undefined-loop-variable
		result_context.append(ll)
	return result_context


def render_line_blocked_context(existed_line_iterator, content_map, marker, gap_line_for_block_marker=False, keep_empty_content_marker=True):
	# type: (Iterator[str], Dict[str, str], BaseLineBlockedMacroMarker, bool, bool) -> List[str]
	"""
	將巨集值放入指定的樣板資料中

	Put macro values into given template content lines and return resulted lines

	Args:
		existed_line_iterator: 要放入巨集值的樣板資料字串迭代器 / String iterator to place macro values into
		content_map: 巨集值的字典物件 / Dictionary contains macro values
		marker: 偵測巨集放置點的標記偵測與產生物件 / Marker detection and generation object
		gap_line_for_block_marker: 是否要在區塊標記與內容間放置一個空白行 / Place a blank line between placed content and block markers
		keep_empty_content_marker: 是否要保留沒有代換內容的標記 / Keep marker of empty content

	Return:
		儲存有已放入巨集資料的字串串列
	"""
	return _render_flat_line_blocked_context(
			_iter_context_line(existed_line_iterator), content_map, marker, gap_line_for_block_marker, keep_empty_content_marker)


def fetch_content_from_line_blocked_context(existed_line_iterator, marker, keep_empty_line=False, keep_empty_content=False):
	# type: (Iterator[str], BaseLineBlockedMacroMarker, bool, bool) -> Dict[str, str]
	""" 從既有已填充樣板資料的內容中取出巨集值

	Pull macro value from filled template content iterator

	Args:
		existed_line_iterator: 要取出巨集值的樣板資料字串迭代器 / String iterator to pull macro values from
		marker: 偵測巨集放置點的標記偵測與產生物件 / Marker detection and generation object
		keep_empty_line=False: 保留空白的行 / Keep empty lines
		keep_empty_content=False: 保留空白的內容 / Keep empty content

	Return:
		儲存有巨集值與鍵的字典物件 / Dictionary object with macro name as key and macro content as value
	"""
	content_map = {}
	in_content_block = False
	indent_text = ""
	indent_len = 0
	block_name = None
	block_content = None
	for l in existed_line_iterator:
		is_trap_line = False
		l = l.rstrip()
		if not in_content_block:
			m = marker.is_trapped_start_line(l)
			if m is None:
				continue
			is_trap_line = True
			indent_text, block_name, _marker_parameter, = m
			indent_len = len(indent_text)
			block_content = []
			in_content_block = True
		if in_content_block:
			m = marker.is_trapped_end_line(l)
			if m is None:
				if is_trap_line:
					continue
				if (l) and (l[0:indent_len] == indent_text):
					l = l[indent_len:]
				if not l:
					l = None
					if not block_content:
						continue
					if (not keep_empty_line) and (block_content[-1] is None):
						continue
				block_content.append(l)
				continue
			is_trap_line = True
			if (
					indent_text,
					block_name,
			) != m:
				_log.warning("unequal block marker parameter: %r, %r != %r", indent_text, block_name, m)
			in_content_block = False
			while (block_content) and (not block_content[-1]):
				block_content.pop()
			if (block_content) or (keep_empty_content is True):
				content_map[block_name] = block_content
			indent_text = ""
			indent_len = 0
			block_name = None
			block_content = None
	return content_map


def put_content_to_line_blocked_file(filepath, content_map, marker, gap_line_for_block_marker=False, keep_empty_content_marker=True):
	# type: (str, Dict[str, str], BaseLineBlockedMacroMarker, bool, bool) -> None
	""" 將巨集值放入指定的樣板檔案中

	Put macro values into given template file

	Args:
		filepath: 要放入巨集值的樣板檔案路徑 / File path to place macro values into
		content_map: 巨集值的字典物件 / Dictionary contains macro values
		marker: 偵測巨集放置點的標記偵測與產生物件 / Marker detection and generation object
		gap_line_for_block_marker: 是否要在區塊標記與內容間放置一個空白行 / Place a blank line between placed content and block markers
		keep_empty_content_marker: 是否要保留沒有代換內容的標記 / Keep marker of empty content
	"""
	with open(filepath, "r") as fp:
		result_context = _render_flat_line_blocked_context(fp, content_map, marker, gap_line_for_block_marker, keep_empty_content_marker)
	with open(filepath, "w") as fp:
		for l in result_context:
			fp.write(l + "\n")


def fetch_content_from_line_blocked_file(filepath, marker, keep_empty_line=False, keep_empty_content=False):
	# type: (str, BaseLineBlockedMacroMarker, bool, bool) -> Dict[str, str]
	""" 將巨集值由指定檔案中取出

	Pull macro values from given file

	Args:
		filepath: 要取出資料的檔案路徑 / Path to fetch template content
		marker: 偵測巨集放置點的標記偵測與產生物件 / Marker detection and generation object
		keep_empty_line=False: 保留空白的行 / Keep empty lines
		keep_empty_content=False: 保留空白的內容 / Keep empty content
	"""
	with open(filepath, "r") as fp:
		content_map = fetch_content_from_line_blocked_context(fp, marker, keep_empty_line, keep_empty_content)
	return content_map


# pylint: disable=too-many-arguments
def replace_context_in_line_blocked_file(filepath,
											context_line_iterator,
											marker,
											gap_line_for_block_marker=False,
											keep_empty_content_marker=True,
											keep_empty_line=False):
	# type: (str, Iterator[str], BaseLineBlockedMacroMarker, bool, bool, bool) -> None
	""" 將巨集值由指定檔案中取出後，將給定的樣板資料套用巨集值後存回指定檔案

	Apply given content with pulled macro values from given file then save back

	Args:
		filepath: 要取出與存回的檔案路徑 / Path to fetch and save back template content
		context_line_iterator: 要放入巨集值的樣板資料字串迭代器 / String iterator to place macro values into
		marker: 偵測巨集放置點的標記偵測與產生物件 / Marker detection and generation object
		gap_line_for_block_marker: 是否要在區塊標記與內容間放置一個空白行 / Place a blank line between placed content and block markers
		keep_empty_content_marker: 是否要保留沒有代換內容的標記 / Keep marker of empty content
		keep_empty_line=False: 保留空白的行 / Keep empty lines
	"""
	if is_path_exists(filepath):
		with open(filepath, "r") as fp:
			existed_content_map = fetch_content_from_line_blocked_context(fp, marker, keep_empty_line)
	else:
		existed_content_map = {}
	result_context = render_line_blocked_context(context_line_iterator, existed_content_map, marker, gap_line_for_block_marker, keep_empty_content_marker)
	with open(filepath, "w") as fp:
		for l in result_context:
			fp.write(l + "\n")


def fetch_digest_from_lined_file(filepath, digest_marker):
	# type: (str, BaseLineDigestMarker) -> Optional[str]
	""" 從檔案中取出樣板的雜湊值 / Fetch digest code from file

	Args:
		filepath: 要取出樣板雜湊值的檔案路徑 / Path to fetch digest of template content
		digest_marker: 雜湊值標記偵測與產生物件 / Marker object of template content digest

	Return:
		雜湊值的字串，或是 None 當無法偵測到 / String of digest code or None if cannot detected
	"""
	with open(filepath, "r") as fp:
		for l in fp:
			aux = digest_marker.is_trapped_digest_line(l)
			if aux is not None:
				_indent_text, digest_code, _marker_parameter, = aux
				return digest_code
	return None


# pylint: disable=too-many-arguments
def digest_checked_replace_context_in_line_blocked_file(filepath,
														context_line_iterator,
														digest_marker,
														macro_marker,
														gap_line_for_block_marker=False,
														keep_empty_content_marker=True):
	# type: (str, Iterator[str], BaseLineDigestMarker, BaseLineBlockedMacroMarker, bool, bool) -> None
	""" 檢查給定樣板資料雜湊直是不是有變動，如有變動將巨集值由指定檔案中取出後，將給定的樣板資料套用巨集值後存回指定檔案

	Check if digest of given template is changed.
	If digest code is changed, apply given content with pulled macro values from given file then save back

	Args:
		filepath: 要取出與存回的檔案路徑 / Path to fetch and save back template content
		context_line_iterator: 要放入巨集值的樣板資料字串迭代器 / String iterator to place macro values into
		digest_marker: 偵測雜湊值標記偵測與產生物件 / Digest marker detection and generation object
		macro_marker: 偵測巨集放置點的標記偵測與產生物件 / Macro marker detection and generation object
		gap_line_for_block_marker: 是否要在區塊標記與內容間放置一個空白行 / Place a blank line between placed content and block markers
		keep_empty_content_marker: 是否要保留沒有代換內容的標記 / Keep marker of empty content
	"""
	existed_digest_code = fetch_digest_from_lined_file(filepath, digest_marker) if is_path_exists(filepath) else None
	context_digest_code = _digest_context_line(context_line_iterator)
	if context_digest_code == existed_digest_code:
		return
	replace_context_in_line_blocked_file(filepath, _iter_digest_marked_context_line(context_line_iterator, context_digest_code, digest_marker), macro_marker,
											gap_line_for_block_marker, keep_empty_content_marker)


# vim: ts=4 sw=4 ai nowrap
