# -*- coding: utf-8 -*-
""" Git helper routines """

from commonutil.runprogram import stdout_of_command


def is_clean():
	_data_stdout, retcode, = stdout_of_command("git", "diff", "--quiet")
	if retcode == 0:
		return True
	elif retcode == 1:
		return False
	raise ValueError("unrecognized return code: %r" % (retcode, ))


def get_parent_rev():
	data_stdout, _retcode, = stdout_of_command("git", "rev-parse", "HEAD^")
	return data_stdout.strip()


def get_current_rev():
	data_stdout, _retcode, = stdout_of_command("git", "rev-parse", "HEAD")
	return data_stdout.strip()


# vim: ts=4 sw=4 ai nowrap
