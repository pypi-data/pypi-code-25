from django.test import TestCase

from ..models import HoardFile
from . import TESTFILE, TESTFILE_MD5


class TestHoardFile(TestCase):
    def test(self):
        hf = HoardFile(path=TESTFILE)
        hf.update()
        hf.save()
        self.assertEqual(hf.md5, TESTFILE_MD5)
