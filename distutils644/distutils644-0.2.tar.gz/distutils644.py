# encoding=UTF-8

# Copyright © 2011-2018 Jakub Wilk <jwilk@jwilk.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
Monkey-patch distutils to normalize metadata in generated tarballs:
- ownership (root:root),
- permissions (0644 or 0755),
- order of directory entries (sorted),
- tar format (ustar).

To enable normalization opportunistically, add this to setup.py:

   try:
       import distutils644
   except ImportError:
       pass
   else:
       distutils644.install()
'''

import distutils.archive_util
import os
import sys
import tarfile
import types

if sys.version_info < (2, 7) or ((3, 0) <= sys.version_info < (3, 2)):
    raise ImportError('Python 2.7 or 3.2+ is required')

def install():

    def root_filter(tarinfo):
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = 'root'
        tarinfo.mode &= 0o700
        tarinfo.mode |= 0o644
        if tarinfo.mode & 0o100:
            tarinfo.mode |= 0o111
        return tarinfo

    class TarFile644(tarfile.TarFile):

        format = tarfile.USTAR_FORMAT

        def add(self, name, arcname=None, recursive=True, exclude=None, filter=None):  # pylint: disable=arguments-differ,redefined-builtin
            del filter
            kwargs = {}
            if exclude is not None:
                kwargs.update(exclude=exclude)
            return tarfile.TarFile.add(self,
                name=name,
                arcname=arcname,
                recursive=recursive,
                filter=root_filter,
                **kwargs
            )

    _orig_os_listdir = os.listdir
    def os_listdir(path):
        return sorted(_orig_os_listdir(path))

    def make_tarball(*args, **kwargs):
        orig_os_listdir = os.listdir
        orig_sys_modules = sys.modules.copy()
        tarfile_mod = types.ModuleType('tarfile644')
        tarfile_mod.open = TarFile644.open
        sys.modules['tarfile'] = tarfile_mod
        os.listdir = os_listdir
        try:
            return distutils.archive_util.make_tarball(*args, **kwargs)
        finally:
            os.listdir = orig_os_listdir
            sys.modules.clear()
            sys.modules.update(orig_sys_modules)

    def patch_format(fmt):
        if fmt[0] is distutils.archive_util.make_tarball:
            return (make_tarball,) + fmt[1:]
        return fmt

    archive_formats = distutils.archive_util.ARCHIVE_FORMATS
    archive_formats = dict(
        (key, patch_format(value))
        for key, value
        in archive_formats.items()
    )
    distutils.archive_util.ARCHIVE_FORMATS = archive_formats

__version__ = '0.2'

__all__ = ['install']

# vim:ts=4 sts=4 sw=4 et
