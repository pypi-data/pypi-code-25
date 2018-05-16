# -*- coding: utf-8 -*-
""" Mercurial helper routines """

from commonutil.runprogram import stdout_of_command


def is_clean():
	data_stdout, retcode, = stdout_of_command("hg", "identify", "--id")
	if retcode != 0:
		raise ValueError("return code is not 0: %r" % (retcode, ))
	l = data_stdout.strip()
	if l[-1] == "+":
		return False
	return True


def get_parent_rev():
	data_stdout, _retcode, = stdout_of_command("hg", "parent", "--rev", "parents()", "--template", "{rev}:{node}\\n")
	aux = data_stdout.split("\n")
	return aux[0].strip()


def get_current_rev():
	data_stdout, _retcode, = stdout_of_command("hg", "parent", "--template", "{rev}:{node}\\n")
	return data_stdout.strip()


# vim: ts=4 sw=4 ai nowrap
