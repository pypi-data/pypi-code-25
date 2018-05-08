# -*- coding: utf-8 -*-

'''
@author: Gabriele Girelli
@contact: gigi.ga90@gmail.com
@description: methods for arguments manipulation.
'''

# DEPENDENCIES =================================================================

import datetime
import multiprocessing
import sys

# CONSTANTS ====================================================================

# FUNCTIONS ====================================================================

def check_threads(threads):
    # Check thread count
    if threads <= 0: return(1)
    if threads > multiprocessing.cpu_count():
        return(multiprocessing.cpu_count())
    return(threads)

def export_settings(OH, ssettings, cmd = True, timestamp = True, pyver = True):
	'''Writes settings strings to file, with command line, timestamp and Python
	version.

	Args:
		OH (file): pointer to output buffer file for writing.
		ssettings (str): settings string.
		cmd (bool): include command line.
		timestamp (bool): include timestamp.
		pyver (bool): include Python version.
	'''
	OH.write("%s\n" % " ".join(sys.argv))
	OH.write("@%s\n\n" % datetime.datetime.now())
	OH.write("Python %s\n\n" % sys.version)
	OH.write(ssettings)

# END ==========================================================================

################################################################################
