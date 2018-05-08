# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: methods for question prompt.
'''

# DEPENDENCIES =================================================================

import sys

# CONSTANTS ====================================================================

# FUNCTIONS ====================================================================

def ask(q):
	"""Ask for confirmation. Aborts otherwise.

	Args:
		q (string): question.
	"""
	answer = ''
	while not answer.lower() in ['y', 'n']:
		print("%s %s" % (q, "(y/n)"))
		answer = sys.stdin.readline().strip()

		if 'n' == answer.lower():
			sys.exit("Aborted.\n")
		elif not 'y' == answer.lower():
			print("Please, answer 'y' or 'n'.\n")
	print("")

# END ==========================================================================

################################################################################
