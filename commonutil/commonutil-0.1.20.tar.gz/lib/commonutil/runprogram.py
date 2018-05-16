# -*- coding: utf-8 -*-
""" 執行程式相關輔助函式 / Program invoking helpers """

import subprocess


def stdout_of_command(*cmd):
	# type: (*str) -> Tuple[str, int]
	"""
	執行給定的指令，並留存 STDOUT 的輸出並傳回。須注意因內容為儲存於記憶體中，因此程式如果有大量輸出可能會造成記憶體用盡。

	Run given command and return the content of STDOUT.
	Caution: The content of STDOUT is kept in memory. Memory might be exhausted if the command generates huge amount of output.

	Args:
		*cmd: 要執行的指令 / Command to invoke

	Return:
		一個 (data_stdout, retcode,) 形式的 tuple 物件，分別表示程式輸出到 STDOUT 的內容，以及程式結束時的傳回碼。

		Tuple object in (data_stdout, retcode,) form. The resulted tuple represents output in STDOUT and the return code of given command respectively.
	"""
	pobj = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	data_stdout, _data_stderr, = pobj.communicate()
	retcode = pobj.returncode
	return (data_stdout, retcode)


# vim: ts=4 sw=4 ai nowrap
