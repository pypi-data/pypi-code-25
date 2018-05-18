import os
import sys
import yaml

from cam.source import Tarball,Git
from cam.utils import console,shell
from cam.errors import FatalError
from testutils import TestCase

import shutil
import json
import io
from contextlib import redirect_stdout

class TestEnviroment(TestCase):

    def test_general_only(self):
        
        console.capturer.open()
        
        os.chdir(self.pathOf('','data'))
        f = io.StringIO()
        with redirect_stdout(f):
            self.dispatch([
            'build',
            '--file','enviroment.yml ',
            '--project', 'general_only',
            '--configure'
            ])
        logs = f.getvalue()
        console.capturer.close()
        env = json.loads(logs)
        
        self.assertEqual(env["VAR1"], "gc.enviroment.VAR1") 
        self.assertEqual(env["VAR2"], "gc.enviroment.VAR2") 
        self.assertEqual(env["VAR3"], "gc.enviroment.VAR3") 
        self.assertEqual(env["VAR4"], "gc.enviroment.VAR4")



    def test_project_append(self):
        
        console.capturer.open()
        
        os.chdir(self.pathOf('','data'))
        f = io.StringIO()
        with redirect_stdout(f):
            self.dispatch([
            'build',
            '--file','enviroment.yml ',
            '--project', 'project_append',
            '--configure'
            ])
        logs = f.getvalue()
        console.capturer.close()
        env = json.loads(logs)
        
        self.assertEqual(env["VAR1"], "gc.enviroment.VAR1") 
        self.assertEqual(env["VAR2"], "gc.enviroment.VAR2") 
        self.assertEqual(env["VAR3"], "gc.enviroment.VAR3") 
        self.assertEqual(env["VAR4"], "gc.enviroment.VAR4")
        self.assertEqual(env["VAR5"], "project_append.VAR5")


    def test_project_overwrite(self):
        
        console.capturer.open()
        
        os.chdir(self.pathOf('','data'))
        f = io.StringIO()
        with redirect_stdout(f):
            self.dispatch([
            'build',
            '--file','enviroment.yml ',
            '--project', 'project_overwrite',
            '--configure'
            ])
        logs = f.getvalue()
        console.capturer.close()
        env = json.loads(logs)
        
        self.assertEqual(env["VAR1"], "project_overwrite.VAR1") 
        self.assertEqual(env["VAR2"], "project_overwrite.VAR2") 
        self.assertEqual(env["VAR3"], "project_overwrite.VAR3") 
        self.assertEqual(env["VAR4"], "project_overwrite.VAR4")

    def test_step(self):
        
        console.capturer.open()
        
        os.chdir(self.pathOf('','data'))
        f = io.StringIO()
        with redirect_stdout(f):
            self.dispatch([
            'build',
            '--file','enviroment.yml ',
            '--project', 'step',
            '--configure'
            ])
        logs = f.getvalue()
        console.capturer.close()
        env = json.loads(logs)
        
        self.assertEqual(env["VAR9"], "configure.VAR9")