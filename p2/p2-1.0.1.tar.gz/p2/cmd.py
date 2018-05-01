#!/usr/bin/env python
#
# Run the given commands if one of the files is motified
#
# Author: keitheis
# Date: 2012-04-24
#
import os
import re
import sys
import logging
import time
from subprocess import call
from pprint import pformat

_ignore_targets = []
_ignore_extensions = ['pyc', 'swp', 'swo',
                      'bmp', 'jpg', 'jpeg',
                      'png', 'gif', 'svg', 'psd', 'xcf', 'pxm']
monitored_files = {}

CHANGED = True


def get_mtime(filepath, mtime=0):
    """
    Get motified time of a file(path)
    """
    OK = False
    tried = 0
    while not OK and tried < 5:
        try:
            stat = os.stat(filepath)
            if stat:
                mtime = stat.st_mtime
            else:
                mtime = 0
            OK = True
        except (OSError, IOError):
            logging.warn('Give up %s' % filepath)
            tried += 1

    if not tried < 5:
        return None
    return mtime


def udpate_mtime(files):
    """
    Check if file is motified, return a boolean value
    """
    change_flag = None

    for file in files:
        mtime = get_mtime(file)

        if mtime is None:
            del monitored_files[file]
            continue

        if file not in monitored_files:
            monitored_files[file] = mtime
        elif monitored_files[file] < mtime:
            print("%s changed" % file)
            monitored_files[file] = mtime
            change_flag = True

    return change_flag


def run_commands(callback_commands):
    """
    Run the given commands if one of the files is motified
    """
    for command in callback_commands:
        print(command)
        call(command, shell=True)
    print("CONTINUE?")


def scan_dir(path):
    """
    Scan the given path, add files under that path into list
    """
    allfiles = []
    for path, dirs, files in os.walk(path):
        for f in files:
            allfiles.append(os.path.join(path, f))
    return allfiles


def gather_files(path):
    """
    Collect the files of given path
    """
    files = []
    if not os.path.exists(path):
        return files

    if os.path.isdir(path):
        files += scan_dir(path)
    else:
        files.append(path)

    ignore_pattern = re.compile(r'.*\.(' + '|'.join(_ignore_extensions) + ')$',
                                re.UNICODE | re.IGNORECASE)
    filtered_files = [f for f in files if (not ignore_pattern.match(f)) and
                      f not in _ignore_targets]
    return filtered_files


def main():
    if len(sys.argv) < 3:
        helpdoc = """Usage:
    {0} 'command' [monitor_path [monitored_path...]]
    e.g.
    {0} 'pytest app/tests' app/
 """.format(sys.argv[0].split("/")[-1])
        print(helpdoc)
        return

    global _ignore_targets
    _ignore_targets = []
    cmd = sys.argv[1]
    files = []

    # collect files' path
    for i in range(2, len(sys.argv)):  # arguments of files' path
        target = sys.argv[i]
        got_files = gather_files(target)
        files += got_files

    for file in files:
        monitored_files[file] = get_mtime(file)
    callback_commands = []
    callback_commands.append(cmd)
    argstr = ''
    for i in range(2, len(sys.argv)):
        argstr += ' %s' % sys.argv[i]
    print("Player Two is watching about %d files:\n%s" % (
        len(monitored_files), pformat(argstr))
    )

    # run commands right away for first time executed
    change_flag = True
    while 1:
        if change_flag:
            print("FIGHT!")
            run_commands(callback_commands)
        change_flag = udpate_mtime(monitored_files)
        time.sleep(1)


def script_entrypoint():
    try:
        main()
    except KeyboardInterrupt as e:
        print("GAMEOVER")


if __name__ == '__main__':
    script_entrypoint()
