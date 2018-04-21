from django.test import TestCase
from django.core.files.base import ContentFile
from ..storage import PackratStorage


class TestPackratStorage(TestCase):

    def test_save(self):
        storage = PackratStorage('blah:')
        contents = b'blahlbh'
        path = storage.save('/some/path', ContentFile(contents))
        storage.open(path)
