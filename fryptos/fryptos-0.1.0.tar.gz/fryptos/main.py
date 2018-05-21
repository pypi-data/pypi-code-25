"""File path encryption.

Put files to public directory by encryption.
And this anchers of relationship.
This module anable change the anchers.
"""
import glob
import logging
import os
import shutil
import filename
from anchor.anchor import Anchor


def main(src, dst):
    """Main script of this code."""
    # Currently, you can use only `text` type ;)
    anchor = Anchor('text')
    for org_f in _read_files(src):
        cur_f = anchor.request_current_path(org_f)
        # WARNING: Theoritically, encrypted files have very low possibility which 
        #          have collision file name, and this script does not check duplication of
        #          file name.
        enc_f = _make_dest_dir(dst, _encrypt_file(org_f, anchor))

        logging.debug('---')
        logging.debug('Original: {0}'.format(org_f))
        logging.debug('Current: {0}'.format(cur_f))
        logging.debug('Encrypt: {0}'.format(enc_f))

        # TODO: Add transaction process.
        _copy(org_f, enc_f)
        anchor.change(org_f, enc_f) # Write the change to anchor file
        if cur_f and os.path.exists(cur_f):
            _delete(dst, cur_f)


def _read_files(file_path):
    """Read all target files with generator."""
    for r, d, fs in os.walk(file_path):
        for f in fs:
            print( os.path.join(r, f))
            yield os.path.join(r, f)


def _encrypt_file(fname, anchor):
    """Encrypt file name."""
    return filename.change(fname)


def _make_dest_dir(public_dir, file_path):
    """Create destination directory."""
    return os.path.join(public_dir, file_path)


def _copy(org_f, enc_f):
    """Copy source file into destination file."""
    os.makedirs('/'.join(enc_f.split('/')[0:-1]))
    shutil.copy(org_f, enc_f)


def _delete(dst_dir, cur_f):
    """Delete old encrypt file"""
    delete_base_path = cur_f.replace(dst_dir.rstrip('/')+'/', '')
    delete_path = os.path.join(dst_dir, delete_base_path.split('/')[0])
    shutil.rmtree(delete_path)
    logging.debug('Delete: {}'.format(delete_path))


def execute():
    import argparse
    from os.path import expanduser
    from os.path import isdir

    home_dir = expanduser('~')
    p = argparse.ArgumentParser(description='Encrypt files.')
    # source and destination is necessary argument.
    p.add_argument('source', help='Source directory')
    p.add_argument('destination', help='destination of encrypttion.')
    # debug mode.
    p.add_argument('-v', help='Verbose mode.', dest='verbose', action='count', default=0)

    args = p.parse_args()
    src = str(args.source)
    dst = str(args.destination)

    if not isdir(src):
        print('No such directory \'{}\'.'.format(src))
        quit()
    if not isdir(dst):
        print('No such directory \'{}\'.'.format(dst))
        quit()
    
    verbose = args.verbose
    if isinstance(verbose, int) and verbose > 0:
        log_format = '%(asctime)s\t[%(levelname)s]\t%(message)s'
        logging.basicConfig(level=10, format=log_format)

    main(src, dst)

if __name__ == '__main__':
    execute()
