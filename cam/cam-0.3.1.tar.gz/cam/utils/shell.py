# cerbero - a multi-platform build system for Open Source software
# Copyright (C) 2012 Andoni Morales Alastruey <ylatuya@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import logging
import subprocess
import shlex
import sys
import os
import re
import tarfile
import zipfile
import tempfile
import time
import glob
import shutil
import hashlib
import urllib.request, urllib.error, urllib.parse
from distutils.version import StrictVersion

from cam.utils.console import call,check_call
from cam.sysinfo import PLATFORM
from cam.enums import Platform,Architecture

PATCH = 'patch'
TAR = 'tar'







def apply_patch(patch, directory, strip=1):
    '''
    Apply a patch

    @param patch: path of the patch file
    @type patch: str
    @param directory: directory to apply the apply
    @type: directory: str
    @param strip: strip
    @type strip: int
    '''

    logging.info("Applying patch %s" % (patch))
    call('%s -p%s -f -i %s' % (PATCH, strip, patch), directory)



def _splitter(string, base_url):
    lines = string.split('\n')
    for line in lines:
        try:
            yield "%s/%s" % (base_url, line.split(' ')[2])
        except:
            continue




def ls_files(files, prefix):
    if files == []:
        return files
    sfiles = check_call('ls %s' % ' '.join(files),
                        prefix, True, False, False).split('\n')
    sfiles.remove('')
    return list(set(sfiles))


def ls_dir(dirpath, prefix):
    files = []
    for root, dirnames, filenames in os.walk(dirpath):
        _root = root.split(prefix)[1]
        if _root[0] == '/':
            _root = _root[1:]
        files.extend([os.path.join(_root, x) for x in filenames])
    return files




def replace(filepath, replacements):
    ''' Replaces keys in the 'replacements' dict with their values in file '''
    with open(filepath, 'r') as f:
        content = f.read()
    for k, v in replacements.items():
        content = content.replace(k, v)
    with open(filepath, 'w+') as f:
        f.write(content)


def find_files(pattern, prefix):
    return glob.glob(os.path.join(prefix, pattern))


def prompt(message, options=[]):
    ''' Prompts the user for input with the message and options '''
    if len(options) != 0:
        message = "%s [%s] " % (message, '/'.join(options))
    res = input(message)
    while res not in [str(x) for x in options]:
        res = input(message)
    return res


def prompt_multiple(message, options):
    ''' Prompts the user for input with using a list of string options'''
    output = message + '\n'
    for i in range(len(options)):
        output += "[%s] %s\n" % (i, options[i])
    res = input(output)
    while res not in [str(x) for x in range(len(options))]:
        res = input(output)
    return options[int(res)]


def copy_dir(src, dest):
    if not os.path.exists(src):
        return
    for path in os.listdir(src):
        s = os.path.join(src, path)
        d = os.path.join(dest, path)
        if not os.path.exists(os.path.dirname(d)):
            os.makedirs(os.path.dirname(d))
        if os.path.isfile(s):
            shutil.copy(s, d)
        elif os.path.isdir(s):
            copy_dir(s, d)


def touch(path, create_if_not_exists=False, offset=0):
    if not os.path.exists(path):
        if create_if_not_exists:
            open(path, 'w').close()
        else:
            return
    t = time.time() + offset
    os.utime(path, (t, t))


def file_hash(path):
    '''
    Get the file md5 hash
    '''
    return hashlib.md5(open(path, 'rb').read()).digest()



def which(pgm, path=None):
    if path is None:
        path = os.getenv('PATH')
    for p in path.split(os.path.pathsep):
        p = os.path.join(p, pgm)
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
        if PLATFORM == Platform.WINDOWS:
            for ext in os.getenv('PATHEXT').split(';'):
                pext = p + ext
                if os.path.exists(pext):
                    return pext



def download(url, destination=None, check_cert=False, overwrite=False):
    import urllib
    import logging

    ctx = None
    if not check_cert:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    # This is roughly what wget and curl do
    if not destination:
        destination = os.path.basename(url)

    if not overwrite and os.path.exists(destination):
        return
    if not os.path.exists(os.path.dirname(destination)):
        os.makedirs(os.path.dirname(destination))

    logging.info("Downloading %s", url)
    try:
        logging.info(destination)
        with open(destination, 'wb') as d:
            f = urllib.request.urlopen(url, context=ctx)
            d.write(f.read())
    except urllib.error.HTTPError as e:
        if os.path.exists(destination):
            os.remove(destination)
        raise e

def rmtree( path ):
    if PLATFORM == Platform.WINDOWS:
        call('del /S/Q/F %s'%path.replace('/','\\'))
    else:
        shutil.rmtree(path)