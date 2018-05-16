# -*- coding: utf-8 -*-
""" 檔案與資料夾輔助函式 / File and folder management routines """

import os
from os.path import isdir
from os.path import abspath
from os.path import join as path_join
from collections import Iterable
import stat
import logging
_log = logging.getLogger(__name__)

DEFAULT_FOLDER_MODEBITS = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH

FOLDER_CHECKBITS = os.R_OK | os.W_OK | os.X_OK


def chmod_folders(folder_path, mode=DEFAULT_FOLDER_MODEBITS):
	# type: (str, int) -> None
	"""
	變更資料夾與子資料夾的存取模式

	Modify access bits of given folder recursively

	Args:
		folder_path: 資料夾路徑 / Folder path
		mode=DEFAULT_FOLDER_MODEBITS: 要設定的存取模式 / Access mode bits
	"""
	for root, dirs, _files in os.walk(folder_path):
		for d in dirs:
			os.chmod(os.path.join(root, d), mode)


def make_folders(folder_path, mode=DEFAULT_FOLDER_MODEBITS):
	# type: (str, int) -> bool
	"""
	準備/建立資料夾，當資料夾不存在時試圖建立資料夾

	Make folder recursively with given access mode bit.

	Args:
		folder_path: 要建立的資料夾路徑 / Path of folder to create

	Return:
		True 當資料夾已存在或建立成功且可讀寫，或是 False 當資料夾存在但可能無法存取，若無法建立資料夾則會丟出例外

		True if folder is successfully created and able to RWX.
		False if folder is created but may not able to RWX.
		An exception will be raised if failed to create folder.
	"""
	if isdir(folder_path):
		if os.access(folder_path, FOLDER_CHECKBITS):
			return True
		os.chmod(folder_path, mode)
		if os.access(folder_path, FOLDER_CHECKBITS):
			return True
		return False
	ioe = None
	try:
		if not isdir(folder_path):
			os.makedirs(folder_path, mode)
	except Exception as e:
		_log.exception("cannot make folder: %r", folder_path)
		ioe = e
	if os.path.isdir(folder_path):
		return os.access(folder_path, FOLDER_CHECKBITS)
	if ioe is not None:
		raise ioe  # pylint: disable=raising-bad-type
	raise ValueError("cannot have folder prepared: %r" % (folder_path, ))


def overwrite_file(filepath_dst, filepath_src, unlink_source_file=False):
	# type (str, str, bool) -> None
	"""
	將指定的檔案用給定的檔案內容覆寫，然後刪除內容來源檔案

	Overwrite target file content with given source file

	Args:
		filepath_dst: 要覆寫內容的檔案 / File to be overwritten
		filepath_src: 內容來源的檔案 / File provides content
	"""
	with open(filepath_src, "rb") as fp_f, open(filepath_dst, "wb") as fp_t:
		fp_t.truncate(0)
		content = fp_f.read(2048)
		while content:
			fp_t.write(content)
			content = fp_f.read(2048)
	if unlink_source_file:
		os.unlink(filepath_src)


def rotate_file(filepath, preserve=9):
	# type: (str, int) -> None
	"""
	將最舊的檔案刪除，並備份目前的檔案

	Delete eldest file and backup current file.

	Args:
		filepath: 要備份的檔案 / File to backup
		preserve=9: 保留的備份數 / Copies to be reserved
	"""
	if preserve < 1:
		preserve = 1
	target_filepath = filepath + "." + str(preserve)
	if os.path.exists(target_filepath):
		os.unlink(target_filepath)
	while preserve > 1:
		preserve = preserve - 1
		moving_filepath = filepath + "." + str(preserve)
		if os.path.exists(moving_filepath):
			os.rename(moving_filepath, target_filepath)
		target_filepath = moving_filepath
	overwrite_file(target_filepath, filepath, unlink_source_file=False)


def _flatten_path_component(iterable):
	for v in iterable:
		if isinstance(v, basestring):
			yield v
		elif isinstance(v, Iterable):
			for v1 in _flatten_path_component(v):
				yield v1
		else:
			_log.warning("unable to recognize path component: %r", v)


def absjoin(*args):
	# type: (*str) -> str
	"""
	由基底資料夾路徑與相對的檔案路徑建立絕對的檔案路徑

	Make absolute path from path components

	Args:
		*args: 基底資料夾路徑與相對於基底資料夾的檔案路徑等路徑元素 / path components

	Return:
		組合後的絕對路徑 / absolute path to file
	"""
	p = list(_flatten_path_component(args))
	return abspath(path_join(*p))


# vim: ts=4 sw=4 ai nowrap
