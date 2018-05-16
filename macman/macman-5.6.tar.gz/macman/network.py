#!/usr/bin/python
# Filename: network.py

from subprocess import Popen, PIPE
import macman
import re


# TODO: Put in some error management with the mounting
def mountNetworkVolume(path, username=None, password=None):
    """ Mount a network share """
    args = 'mount volume "%s" ' % path
    if username and password:
        args += 'as user name "%s" with password "%s"' % (username, password)
    output = macman.misc.osascript(args)

    return output


def listAvailableShares(path):
    """ List of advertised shared volumes on a network share """

    args = ['/usr/bin/smbutil', 'view', '-g', '//%s' % path]

    p = Popen(args, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()

    available_shares = []
    for line in output.split('\n'):
        if 'Disk' in line:
            available_shares.append(line.split('Disk')[0].strip())

    return available_shares


def listMountedShares():
    """ Return a dictionary of tuples containing mounted shared volumes on a network share

    Example:
        mounted_shares = listMountedShares()

    """

    args = ['/sbin/mount', '-t', 'smbfs,afpfs']

    p = Popen(args, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()

    mounted_shares = {}

    output = output.strip().split('\n')
    for line in output:
        share_user = line.split()[0].split('@')[0][2:]
        share_server = line.split()[0].split('@')[1].split('/')[0]
        share_name = line.split()[0].split('@')[1].split('/')[1]
        share_name = re.sub('%20', ' ', share_name)
        share_mount_path = line.split()[2]
        mounted_shares[share_server] = {}
        mounted_shares[share_server][share_name] = {}
        mounted_shares[share_server][share_name] = (share_mount_path, share_user)

        return mounted_shares
