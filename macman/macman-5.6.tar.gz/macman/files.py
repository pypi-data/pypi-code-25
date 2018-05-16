#!/usr/bin/python
# Filename: files.py

import os
import stat
import macman
import tempfile
import shutil

def getPathPermissions(path):
    """
    Retrieve current uid, gid, and mode for a path,

    Returns a dictionary in format { 'uid': <uid>, 'gid': <gid>, 'mode': <mode> }
    """

    # if path exists, get current permissions
    if os.path.isfile(path):
        stat_info = os.stat(path)
        uid = stat_info.st_uid
        gid = stat_info.st_gid
        mode = oct(stat.S_IMODE(os.lstat(path).st_mode))

    # if path does not exist
    else:
        uid = None
        gid = None
        mode = None

    return {'uid': uid, 'gid': gid, 'mode': mode}


def setPathPermissions(path, mode):
    """Set permissions for a path. If path is a directory, set permissions recursively.

    Permissions are in octal mode format (ie 0755).

    If path does not exist, an exception is raised.

    Example:
        setPathPermissions('/tmp', '0755')

    """

    abs_path = os.path.abspath(path)

    # convert from octal to decimal
    mode = int(str(mode), 8)

    if os.path.exists(abs_path):
        try:
            # if is a directory, set permissions recursively
            if os.path.isdir(abs_path):
                os.chmod(abs_path, mode)
                for root, dirs, files in os.walk(abs_path):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), mode)
                    for f in files:
                        os.chmod(os.path.join(root, f), mode)
            else:
                os.chmod(abs_path, mode)
        except OSError:
            pass
    
    # if path does not exist
    else:
        raise OSError("[Errno 2] No such file or directory, %s" % abs_path)


def setPathUidGid(path, uid, gid):
    """ Set uid and guid for a file path """

    if os.path.isfile(path):

        # Set uid and gid
        macman.logs.writeLog('Setting uid: %s and gid: %s on %s' % (str(uid), str(gid), path))
        os.chown(path, int(uid), int(gid))


def createTemporaryCopy(path):
    """ Create tempory copy of a file.
    Useful when a binary plist needs to be read but permissions do not allow conversion to XML"""

    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, 'temp_file_name')
    shutil.copy2(path, temp_path)

    return temp_path




