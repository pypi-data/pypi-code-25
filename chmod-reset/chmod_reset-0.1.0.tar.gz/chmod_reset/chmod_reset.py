# -*- coding: utf-8 -*-
import os

CHMOD_FILE = 0o644 # rw-r--r--
CHMOD_DIR =  0o755 # rwxr-xr-x

def scan(path, verbose=True):
    '''Change recursively folder/file/link permisisons'''
    if os.path.islink(path):
        if verbose:
            print('L > {}'.format(path))
    elif os.path.isfile(path):
        if verbose:
            print('F > {}'.format(path))
        os.chmod(path, CHMOD_FILE)
    elif os.path.isdir(path):
        if verbose:
            print('D > {}'.format(path))
        os.chmod(path, CHMOD_DIR)
        for sub in os.listdir(path):
            scan(os.path.join(path, sub), verbose)
    else:
        raise ValueError('`{}` is neither a file nor a directory'.format(path))
