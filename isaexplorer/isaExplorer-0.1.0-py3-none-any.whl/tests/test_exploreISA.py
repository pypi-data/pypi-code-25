import unittest
import os
import tempfile
from distutils import dir_util

import isaExplorer

pathToISATABFile = os.path.join(os.path.dirname(__file__), 'test_data', 'TestISA')

class TestExploreISA(unittest.TestCase):
    def test_exploreISA(self):
        self.assertIsNone(isaExplorer.exploreISA(pathToISATABFile, verbose=False))

class TestGetISAAssay(unittest.TestCase):
    def test_getISAAssay(self):
        self.assertTrue(isaExplorer.isaExplorer.getISAAssay(1,1,pathToISATABFile))

class TestGetISAStudy(unittest.TestCase):
    def test_getISAStudy(self):
        self.assertTrue(isaExplorer.isaExplorer.getISAStudy(1,pathToISATABFile))

class Test_study_operations(unittest.TestCase):
    def test_AppendStudytoISA(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            pathToTempISATABFile = os.path.join(tmpdirname, 'TestISA')
            dir_util.copy_tree(pathToISATABFile, pathToTempISATABFile)

            study = isaExplorer.isaExplorer.getISAStudy(1,pathToTempISATABFile)
            self.assertIsNone(isaExplorer.isaExplorer.appendStudytoISA(study,pathToTempISATABFile))

    @unittest.expectedFailure
    def test_dropStudyFromISA(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            pathToTempISATABFile = os.path.join(tmpdirname, 'TestISA')
            dir_util.copy_tree(pathToISATABFile, pathToTempISATABFile)

            study = isaExplorer.isaExplorer.getISAStudy(1,pathToTempISATABFile)
            isaExplorer.isaExplorer.appendStudytoISA(study,pathToTempISATABFile)

            self.assertIsNone(isaExplorer.isaExplorer.dropStudyFromISA(2,pathToTempISATABFile))

class Test_assay_operations(unittest.TestCase):
    def test_appendAssayToStudy(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            pathToTempISATABFile = os.path.join(tmpdirname, 'TestISA')
            dir_util.copy_tree(pathToISATABFile, pathToTempISATABFile)

            assay = isaExplorer.isaExplorer.getISAAssay(1,1,pathToTempISATABFile)
            self.assertIsNone(isaExplorer.isaExplorer.appendAssayToStudy(assay,1,pathToTempISATABFile))

    @unittest.expectedFailure
    def test_dropAssayFromStudy(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            pathToTempISATABFile = os.path.join(tmpdirname, 'TestISA')
            dir_util.copy_tree(pathToISATABFile, pathToTempISATABFile)

            assay = isaExplorer.isaExplorer.getISAAssay(1,1,pathToTempISATABFile)
            isaExplorer.isaExplorer.appendAssayToStudy(assay,1,pathToTempISATABFile)

            self.assertIsNone(isaExplorer.isaExplorer.dropAssayFromStudy(2,1,pathToTempISATABFile))
