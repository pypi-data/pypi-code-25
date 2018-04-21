from django.test import TestCase
from django.core.management import call_command

from ..models import HoardFile
from . import TESTFILE, TESTFILE_MD5


class TestUpdateHoard(TestCase):

    def test_single_file(self):
        self.assertFalse(HoardFile.objects.filter(md5=TESTFILE_MD5).exists())
        call_command('update_hoard', TESTFILE)
        self.assertTrue(HoardFile.objects.filter(md5=TESTFILE_MD5).exists())
