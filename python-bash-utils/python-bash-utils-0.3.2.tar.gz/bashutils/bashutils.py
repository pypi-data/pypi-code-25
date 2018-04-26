# -- coding: utf-8 --

# Copyright 2015
#
# This file is part of proprietary software and use of this file
# is strictly prohibited without written consent.
#
# @author  Tim Santor  <tsantor@xstudios.agency>

"""Common methods to help assist when creating bash style python scripts."""

# -----------------------------------------------------------------------------

from __future__ import absolute_import, print_function, unicode_literals

import platform
import shlex
import subprocess

# -----------------------------------------------------------------------------
# Get OS
# -----------------------------------------------------------------------------


def get_os():
    """Returns the current OS name (OSX, Fedora, CentOS, Debian or Ubuntu)."""
    uname = platform.system()
    if uname == 'Darwin':
        return 'OSX'

    if uname == 'Linux':
        find = ['Fedora', 'CentOS', 'Debian', 'Ubuntu']
        # If lsb_release then test that output
        status = exec_cmd('hash lsb_release &> /dev/null')
        if status:
            for search in find:
                status = exec_cmd('lsb_release -i | grep %s > /dev/null 2>&1' % search)
                if status:
                    return search

        # Try to cat the /etc/*release file
        else:
            for search in find:
                status = exec_cmd('cat /etc/*release | grep %s > /dev/null 2>&1' % search)
                if status:
                    return search

    if uname in ['Windows', 'Win32', 'Win64']:
        return 'Windows'

    return 'unknown'

# -----------------------------------------------------------------------------
# Execute Command
# -----------------------------------------------------------------------------


def exec_cmd(cmd):
    """Executes a command and returns the status, stdout and stderror."""
    # call command
    proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # talk with command i.e. read data from stdout and stderr. Store this info in tuple
    stdout, stderr = proc.communicate()

    # wait for terminate. Get return returncode
    ret_code = proc.wait()
    if ret_code == 0:
        status = True
    else:
        status = False

    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()

    return (status, stdout, stderr)


def cmd_exists(program):
    """Returns True if a command exists."""
    cmd = "where" if get_os() == "Windows" else "which"
    (status, stdout, stderr) = exec_cmd('{0} {1}'.format(cmd, program))
    return status

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print(get_os())
    print(cmd_exists('git'))

    status, stdout, stderr = exec_cmd('git --help')
    print(status, stdout, stderr)
