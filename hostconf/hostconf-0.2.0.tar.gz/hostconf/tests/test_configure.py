"""
Unit testing for parts of the hostconf modules.

"""

import os
import sys
import tempfile
import unittest
import subprocess
from test.support import import_module

class A_Loading(unittest.TestCase):

    def test_001_import_pkg(self):
        hostconf = import_module('hostconf')

    def test_002_import_module(self):
        configure = import_module('hostconf.configure')

    def test_003_build_instance(self):
        cfm = import_module('hostconf.configure')
        cfg = cfm.Configure('test_conf')
        self.assertIsNotNone(cfg)


class Infrastructure(unittest.TestCase):

    def setUp(self):
        # redirect stdout to somewhere bogus
        fd, name = tempfile.mkstemp()
        self._tmp_fd = os.fdopen(fd, 'w')
        self._tmp_name = name

        # built the configurator
        cfm = import_module('hostconf.configure')
        self.ctool = cfm.Configure('test_conf_' + self.id(),
                                   tmpdir='tmp_unittest',
                                   debug=True)
        self.assertIsNotNone(self.ctool)

        # configure the output stream
        self.ctool.ostream = self._tmp_fd

    def tearDown(self):
        self._tmp_fd.close()
        os.remove(self._tmp_name)
        self.ctool = None


class BasicChecking(Infrastructure):

    def test_stdc(self):
        self.ctool.check_stdc()

    def test_package_info(self):
        self.ctool.package_info('testing', '1.0', '20180503')

    def test_system_extensions(self):
        self.ctool.check_use_system_extensions()


class Checking(Infrastructure):

    def setUp(self):
        super().setUp()
        
        # basic setups
        self.ctool.package_info('testing', '1.0', '20180503')
        self.ctool.check_stdc()
        self.ctool.check_use_system_extensions()

        # setup the path to the 'test' include dir
        self.inc_dir = os.path.join(os.path.dirname(__file__), 'include')

    
    def test_header(self):
        ok = self.ctool.check_header('stdio.h')
        self.assertTrue(ok)

    def test_header_custom(self):
        ok = self.ctool.check_header('tomato.h', include_dirs=[self.inc_dir])
        self.assertTrue(ok)

    def test_header_bogus(self):
        ok = self.ctool.check_header('super_garbage.h')
        self.assertFalse(ok)

    def test_headers(self):
        oks = self.ctool.check_headers(
            ['apple.h', 'peach.h', 'pineapple.h', 'veg/broccoli.h'],
            include_dirs=[self.inc_dir])
        self.assertTrue(oks[0])
        self.assertTrue(oks[1])
        self.assertFalse(oks[2])
        self.assertTrue(oks[3])
        
    def test_tool(self):
        ok = self.ctool.check_tool('ls', ['-al', '/'])
        self.assertTrue(ok)

    def test_tool_nonexistant(self):
        ok = self.ctool.check_tool('porkchop', ['--seared'])
        self.assertFalse(ok)

    def test_check_lib_stdlibs(self):
        ok = self.ctool.check_lib('strcat')
        self.assertTrue(ok)
        ok = self.ctool.check_lib('dinosaur')
        self.assertFalse(ok)

    def test_check_libm(self):
        ok = self.ctool.check_lib('ceil', 'm')
        self.assertTrue(ok)

    def test_lib_link(self):
        ok = self.ctool.check_lib_link('sqrt', 'm')
        self.assertTrue(ok)

    def test_decl(self):
        ok = self.ctool.check_decl('sprintf', 'stdio.h')
        self.assertTrue(ok)
        ok = self.ctool.check_decl('totally_not_there', 'stdio.h')
        self.assertFalse(ok)
        
    def test_decl_fcn(self):
        ok = self.ctool.check_decl(
            'pick_apple', 'apple.h', include_dirs=[self.inc_dir])
        self.assertTrue(ok)

    def test_decl_macro(self):
        ok = self.ctool.check_decl(
            'HONEYCRISP', 'apple.h', include_dirs=[self.inc_dir],
            main=['int x = HONEYCRISP;']
        )
        self.assertTrue(ok)

    def test_type(self):
        ok = self.ctool.check_type('unsigned long long')
        self.assertTrue(ok)

    def test_type_std(self):
        ok = self.ctool.check_type('off_t', ['stdio.h'])
        self.assertTrue(ok)

    def test_type_custom(self):
        ok = self.ctool.check_type(
            'apple_t', ['apple.h'], include_dirs=[self.inc_dir])
        self.assertTrue(ok)

    def test_struct_member(self):
        ok = self.ctool.check_member('div_t', 'quot')
        self.assertTrue(ok)
        
    def test_struct_member_custom(self):
        ok = self.ctool.check_member(
            'apple_t', 'sweetness',
            includes=['apple.h'], include_dirs=[self.inc_dir])
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
