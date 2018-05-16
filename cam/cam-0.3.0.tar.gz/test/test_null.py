import os
import sys


import cam
from cam.utils import console

from cam.errors import FatalError


from testutils import TestCase

from cam.cli import dispatch
import argparse

class TestNull(TestCase):
    def setUp(self):
       pass

    def test_cmake(self):
        console.capturer.open()
        
        os.chdir(self.pathOf('null/cmake'))
        self.dispatch([
           'build'
           ])
        cmds = console.capturer.calls()
        console.capturer.close()
        for cmd in cmds:
            self.assertTrue(cmd.startswith("cmake"))
    
    def test_nodegyp(self):
        console.capturer.open()
        
        os.chdir(self.pathOf('null/node-gyp'))
        self.dispatch([
           'build'
           ])
        cmds = console.capturer.calls()
        console.capturer.close()
        for cmd in cmds:            
            self.assertTrue(cmd.startswith("node-gyp"))


