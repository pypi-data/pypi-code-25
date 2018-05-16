import os
import sys
import yaml

from cam.source import Tarball,Git
from cam.utils import console,shell
from cam.errors import FatalError
from testutils import TestCase

import shutil

import io
from contextlib import redirect_stdout

class TestCommands(TestCase):
    def setUp(self):
        pass
        #path = self.pathOf('commands.yml','data')
        #self.config = Configuration( path )

    def test_before(self):
        
        console.capturer.open()
        
        os.chdir(self.pathOf('','data'))
        f = io.StringIO()
        with redirect_stdout(f):
            self.dispatch([
            'build',
            '--file','commands.yml ',
            '--project', 'before',
            '--configure'
            ])
        logs = f.getvalue()
        console.capturer.close()

        self.assertIn("before.configure.before",logs)
        
    def test_after(self):
        
        console.capturer.open()
        
        os.chdir(self.pathOf('','data'))
        f = io.StringIO()
        with redirect_stdout(f):
            self.dispatch([
            'build',
            '--file','commands.yml ',
            '--project', 'after',
            '--configure'
            ])
        logs = f.getvalue()
        console.capturer.close()

        self.assertIn("after.configure.after",logs)


    def test_vars(self):
        
        console.capturer.open()
        
        os.chdir(self.pathOf('','data'))
        f = io.StringIO()
        with redirect_stdout(f):
            self.dispatch([
            'build',
            '--file','commands.yml ',
            '--project', 'vars',
            '--configure'
            ])
        logs = f.getvalue()
        console.capturer.close()
        vlist={}
        for log in logs.split('\n'):
            items = log.split('=')
            if len(items) >= 2:
                vlist[items[0].strip()] = items[1].strip()
        self.assertPathEqual( vlist['__directory__'],
        self.pathOf('','data'))

        self.assertEqual( vlist['version'],'0.3.0')

