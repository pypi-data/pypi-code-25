from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms.widgets import URLInput
from django.test import TestCase

from .example_forms import (ExampleBlacklistedPNGForm, ExampleForm,
                            ExampleWhitelistedPNGForm)
from .fields import RemoteImageField


class RemoteImageTestCase(TestCase):
    def setUp(self):
        pass

    def test_bytes_length_correct_on_img_download(self):
        image_url = "https://upload.wikimedia.org/wikipedia/commons/d/d9/Test.png"
        img_bytesio = RemoteImageField().download_and_return_BytesIO(image_url)
        img_length = img_bytesio.getbuffer().nbytes

        self.assertEqual(3118, img_length)

    def test_remote_image_field_with_png(self):
        image_url = "https://upload.wikimedia.org/wikipedia/commons/d/d9/Test.png"
        
        data = {"remote_image": image_url}
        form = ExampleForm(data)   
        self.assertTrue(form.is_valid())

    def test_remote_image_field_with_jpg(self):
        image_url = "https://upload.wikimedia.org/wikipedia/commons/5/5b/Name.jpg"
        
        data = {"remote_image": image_url}
        form = ExampleForm(data)   
        self.assertTrue(form.is_valid())

    def test_remote_image_field_with_gif(self):
        image_url = "https://upload.wikimedia.org/wikipedia/commons/b/bd/Name.gif"
        
        data = {"remote_image": image_url}
        form = ExampleForm(data)   
        self.assertTrue(form.is_valid())

    def test_remote_image_field_with_whitelist_working(self):
        image_url = "https://upload.wikimedia.org/wikipedia/commons/d/d9/Test.png"
        
        data = {"remote_image": image_url}
        form = ExampleWhitelistedPNGForm(data)
        self.assertTrue(form.is_valid())

    def test_remote_image_field_with_blacklist_working(self):
        image_url = "https://upload.wikimedia.org/wikipedia/commons/d/d9/Test.png"
        
        data = {"remote_image": image_url}
        form = ExampleBlacklistedPNGForm(data)
        self.assertFalse(form.is_valid())

    def test_remote_image_field_with_extension_not_on_whitelist(self):
        image_url = "https://upload.wikimedia.org/wikipedia/commons/b/bd/Name.gif"
        
        data = {"remote_image": image_url}
        form = ExampleWhitelistedPNGForm(data)
        self.assertFalse(form.is_valid())
