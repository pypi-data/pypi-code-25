from django.test import TestCase, override_settings
from django.urls import reverse
from django.urls import path

from ..models import HoardFile
from . import TESTFILE, TESTFILE_MD5
from .. import views

urlpatterns = [
    path('md5/<hsh>', views.md5, name='md5'),
]


@override_settings(ROOT_URLCONF='packrat.tests.test_views')
class TestMD5(TestCase):
    def setUp(self):
        hf = HoardFile(path=TESTFILE)
        hf.update()
        hf.save()

    def test(self):
        url = reverse('md5', args=(TESTFILE_MD5,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        with open(TESTFILE, 'rb') as f:
            self.assertEqual(b''.join(response.streaming_content), f.read())
