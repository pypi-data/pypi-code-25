# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2016 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

from contextlib import contextmanager
import glob
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, DIR)
from util import attrs, capture_output  # noqa


@contextmanager
def cwd(dir):
    oldcwd = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(oldcwd)


def run_setup(*args):
    argv = ['setup.py']
    argv.extend(args)
    with attrs(sys, argv=argv):
        with capture_output() as stdout:
            try:
                import setup  # noqa
            except Exception as exc:
                raise Exception('%s\n--- Output:\n%s-----' %
                                (exc, stdout.getvalue()))
            finally:
                try:
                    del sys.modules['setup']
                except Exception:
                    pass


SDIST_FILE_LIST = [
    ('src', [
        ('quark_sphinx_theme', [
            '__init__.py',
            '__version__.py',
            '_lovelace.py',
            '_mixin.py',
            '_sphinxversion.py',
            ('ext', [
                '__init__.py',
                'html_compat.py',
                ('html_rewrite', [
                    '__init__.py',
                    '_features.py',
                    '_setup_pre16.py',
                    'boxes.py',
                    'compat.py',
                    'literal_blocks.py',
                ]),
            ]),
            ('quark', [
                'domainindex.html',
                'genindex-single.html',
                'genindex.html',
                'layout.html',
                'theme.conf',
                'static/quark.css_t',
            ]),
        ]),
    ]),
    ('test', [
        '__init__.py',
        'test_core.py',
        'test_html_rewrite.py',
        'test_html_rewrite_features.py',
        'test_import.py',
        'test_mixin.py',
        'test_sdist.py',
        'test_sphinxversion.py',
        'test_theme.py',
        'util.py',
        ('testdoc-html_rewrite', [
            'conf.py',
            'contents.rst',
            'test_admonition.rst',
            'test_citation.rst',
            'test_footnote.rst',
            'test_literal_block.rst',
            'test_pre_block.rst',
            'test_sidebar.rst',
            'test_topic.rst',
            'test_warning.rst',
        ]),
        ('testdoc-theme', [
            'conf.py',
            'contents.rst',
        ]),
    ]),
    'LICENSE',
    'MANIFEST.in',
    'README.rst',
    'setup.cfg',
    'setup.py',
    'tox.ini',
]


def flatten_file_list(ls):
    for item in ls:
        if isinstance(item, str):
            yield item
        else:
            prefix, subls = item
            for subitem in flatten_file_list(subls):
                yield '%s/%s' % (prefix, subitem)


def verify_zipfile(z, ls, p=1):
    with zipfile.ZipFile(z, mode='r') as arc:
        names = [n.split('/', p)[-1] for n in arc.namelist()]
        for f in flatten_file_list(ls):
            if f not in names:
                yield f


class TestSourceDistContents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.distdir = tempfile.mkdtemp(prefix='tmp-test-sdist')
        try:
            with cwd(os.path.join(DIR, os.pardir)):
                run_setup('egg_info', '--egg-base', cls.distdir,
                          'sdist', '--formats=zip', '--dist-dir', cls.distdir)
            cls.sdist_name = glob.glob(os.path.join(cls.distdir,
                                       'quark-sphinx-theme-*.zip'))[0]
        except:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        if cls.distdir:
            shutil.rmtree(cls.distdir, True)
            cls.distdir = None

    def test_sdist_contents(self):
        missing = list(verify_zipfile(self.sdist_name, SDIST_FILE_LIST))
        if len(missing) != 0:
            self.fail('Missing expected sdist contents:\n' + '\n'.join(missing))

    def test_sdist_no_pyc(self):
        with zipfile.ZipFile(self.sdist_name, mode='r') as arc:
            for name in arc.namelist():
                if name.endswith('.pyc') or name.endswith('.pyo'):
                    self.fail('undesired file in sdist: %s' % name)


if __name__ == '__main__':
    unittest.main()
