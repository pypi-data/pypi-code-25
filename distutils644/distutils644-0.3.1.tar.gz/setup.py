# encoding=UTF-8

# Copyright © 2013-2018 Jakub Wilk <jwilk@jwilk.net>
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
**distutils644** monkey-patches distutils
to normalize metadata in generated archives:

- ownership (root:root),
- permissions (0644 or 0755),
- order of directory entries (sorted),
- tar format (ustar).
'''

import io
import os
import sys

import distutils.core
from distutils.command.sdist import sdist as distutils_sdist

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    bdist_wheel = None

import distutils644

if sys.version_info < (2, 7) or ((3, 0) <= sys.version_info < (3, 2)):
    raise RuntimeError('Python 2.7 or 3.2+ is required')

distutils644.install()

class cmd_sdist(distutils_sdist):

    def maybe_move_file(self, base_dir, src, dst):
        src = os.path.join(base_dir, src)
        dst = os.path.join(base_dir, dst)
        if os.path.exists(src):
            self.move_file(src, dst)

    def make_release_tree(self, base_dir, files):
        distutils_sdist.make_release_tree(self, base_dir, files)
        self.maybe_move_file(base_dir, 'LICENSE', 'doc/LICENSE')

def get_version():
    path = os.path.join('doc/changelog')
    with io.open(path, encoding='UTF-8') as file:
        line = file.readline()
    return line.split()[1].strip('()')

classifiers = '''
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Topic :: Software Development :: Build Tools
'''.strip().splitlines()

def d(**kwargs):
    return {
        k: v
        for k, v in kwargs.items()
        if v is not None
    }

distutils.core.setup(
    name='distutils644',
    version=get_version(),
    license='MIT',
    description='normalize ownership, permissions, order of directory entries and tar format in distutils-generated archives',
    long_description=__doc__.strip(),
    classifiers=classifiers,
    url='http://jwilk.net/software/distutils644',
    author='Jakub Wilk',
    author_email='jwilk@jwilk.net',
    py_modules=['distutils644'],
    cmdclass=d(
        sdist=cmd_sdist,
        bdist_wheel=bdist_wheel,
    ),
)

# vim:ts=4 sts=4 sw=4 et
