import os
import sys
import yaml

from cam.source import Tarball,Git
from cam.utils import console,shell
from cam.errors import FatalError

from testutils import TestCase

import shutil


class TestSource(TestCase):
    def setUp(self):
        #path = self.pathOf('gittestsample.yml','data')
        #self.config = Configuration( path )
        self._WD = os.path.join(
            os.path.dirname(__file__),'tmp/TestSource'
        )
        os.chdir(os.path.dirname(__file__))
        if os.path.exists( self._WD):
            shutil.rmtree(self._WD)
        os.makedirs(self._WD)

        pass

    def test_tarball(self):
        path = self.pathOf('gittestsample.yml','data')
        os.chdir(self._WD)
        self.dispatch([
           'build',
           '--file',path,
           '-p','tarball',
           '--fetch'
           ])
        filename = os.path.join('./gittestsample-tarball','info.yml')
        print(os.path.abspath(filename))
        info = yaml.load(open(filename))
        self.assertEqual(info['tag'],'0.1.0')


    #ef test_git(self):
    #   path = self.pathOf('gittestsample.yml','data')
    #   os.chdir(self._WD)
    #   self.dispatch([
    #      'build',
    #      '--file',path,
    #      '-p','git',
    #      '--fetch'
    #      ])

    #   filename = os.path.join(prj.location,'info.yml')
    #   info = yaml.load(open(filename))
    #   self.assertEqual(info['tag'],'0.1.0')

