# -*- coding: utf-8 -*-
""" 基於程式碼註解的標記規則物件 / Template marker based on code comment  """

import re

from collections import namedtuple

CFamilyCommentMarkerOption = namedtuple("CFamilyCommentMarkerOption", ("comment_character", ))

_CFAMILY_PAIR_COMMENT_END = {
		"/*": " */",
}


class CFamilyCommentMarker(object):
	def __init__(self, trap_text, *args, **kwds):
		# type: (str) -> None
		super(CFamilyCommentMarker, self).__init__(*args, **kwds)
		self.trap_text = trap_text
		self.regex_block_s = re.compile(r'(\s*)(\/\/|\/\*|#|--)\s*\{\{\{\s+' + trap_text + r':\s+([a-zA-Z0-9_-]+)')
		self.regex_block_e = re.compile(r'(\s*)(\/\/|\/\*|#|--)\s*\}\}\}\s+' + trap_text + r':\s+([a-zA-Z0-9_-]+)')
		self.regex_inline = re.compile(r'(\s*)(\/\/|\/\*|#|--)\s+' + trap_text + r':\s+([a-zA-Z0-9_-]+)')
		self.regex_digest = re.compile(r'(\s*)(\/\/|\/\*|#|--)\s+' + trap_text + r':DIGEST\s+([a-f0-9]+)')

	def is_trapped_start_line(self, l):
		# type: (str) -> Optional[Tuple[str, str, Any]]
		"""
		是否偵測到給定的資料列為巨集放置點的開始行

		Check if given content line is start line of content block

		Args:
			l: 要檢查的資料

		Return:
			當為開始行時傳回 (indent_text, block_name, marker_parameter,) 形式的 tuple 物件。
			分別代表: 縮排的空白字元組成的字串、巨集放置點名稱、這個標記的額外的參數物件
			如果不是則傳回 None
		"""
		m = self.regex_block_s.match(l)
		if m is not None:
			indent_text = m.group(1)
			block_name = m.group(3)
			marker_parameter = CFamilyCommentMarkerOption(m.group(2))
			return (indent_text, block_name, marker_parameter)
		m = self.regex_inline.match(l)
		if m is not None:
			indent_text = m.group(1)
			block_name = m.group(3)
			marker_parameter = CFamilyCommentMarkerOption(m.group(2))
			return (indent_text, block_name, marker_parameter)
		return None

	def is_trapped_end_line(self, l):
		# type: (str) -> Optional[Tuple[str, str]]
		"""
		是否偵測到給定的資料列為巨集放置點的結束行

		Check if given content line is end line of content block

		Args:
			l: 要檢查的資料

		Return:
			當為結束行時傳回 (indent_text, block_name,) 形式的 tuple 物件。
			分別代表: 縮排的空白字元組成的字串、巨集放置點名稱
			如果不是則傳回 None
		"""
		m = self.regex_block_e.match(l)
		if m is not None:
			indent_text = m.group(1)
			block_name = m.group(3)
			return (indent_text, block_name)
		m = self.regex_inline.match(l)
		if m is not None:
			indent_text = m.group(1)
			block_name = m.group(3)
			return (indent_text, block_name)
		return None

	def wrap_line(self, l):  # pylint: disable=unused-argument
		# type: (str) -> str
		"""
		針對給定的資料行進行再處理

		Perform extra actions on given line

		Args:
			l: 準備進行再處理的資料行

		Return:
			經過再處理的新資料行，或是 None 如果不需要再處理
		"""
		return None

	def get_one_line_marker(self, block_name, marker_parameter):
		# type: (str, Any) -> str
		"""
		取得單行的巨集放置點標示

		Args:
			block_name: 巨集放置點的名字 / Name of given macro value block
			marker_parameter: 標記參數物件 / Parameter object of marker

		Return:
			表示單行的巨集放置點的字串
		"""
		return marker_parameter.comment_character + " " + self.trap_text + ": " + block_name + _CFAMILY_PAIR_COMMENT_END.get(
				marker_parameter.comment_character, "")

	def get_block_line_markers(self, block_name, marker_parameter):
		# type: (str, Any) -> Tuple[str, str]
		"""
		取得區塊用的巨集放置點標示

		Args:
			block_name: 巨集放置點的名字 / Name of given macro value block
			marker_parameter: 標記參數物件 / Parameter object of marker

		Return:
			一個 (tag_s, tag_e,) 形式的 tuple 物件，內容物件為資料區塊的巨集放置點的表示字串的起點與終點
		"""
		tag_s = marker_parameter.comment_character + " {{{ " + self.trap_text + ": " + block_name + _CFAMILY_PAIR_COMMENT_END.get(
				marker_parameter.comment_character, "")
		tag_e = marker_parameter.comment_character + " }}} " + self.trap_text + ": " + block_name + _CFAMILY_PAIR_COMMENT_END.get(
				marker_parameter.comment_character, "")
		return (tag_s, tag_e)

	def is_trapped_digest_line(self, l):
		# type: (str) -> Optional[Tuple[str, str, Any]]
		"""
		是否為可存有雜湊值的資料行

		Check if given content line is template digest line

		Args:
			l: 要檢查的資料

		Return:
			當為開始行時傳回 (indent_text, digest_code, marker_parameter,) 形式的 tuple 物件。
			分別代表: 縮排的空白字元組成的字串、雜湊碼、這個標記的額外的參數物件
			如果不是則傳回 None
		"""
		m = self.regex_digest.match(l)
		if m is not None:
			indent_text = m.group(1)
			digest_code = m.group(3)
			marker_parameter = CFamilyCommentMarker(m.group(2))
			return (indent_text, digest_code, marker_parameter)
		return None

	def get_digest_line_marker(self, digest_code, marker_parameter):
		# type: (str, Any) -> str
		"""
		取得雜湊值放置點標示

		Args:
			digest_code: 雜湊值 / Digest code of template
			marker_parameter: 標記參數物件 / Parameter object of marker

		Return:
			表示雜湊值的放置點字串
		"""
		return marker_parameter.comment_character + " " + self.trap_text + ":DIGEST " + digest_code + _CFAMILY_PAIR_COMMENT_END.get(
				marker_parameter.comment_character, "")


# vim: ts=4 sw=4 ai nowrap
