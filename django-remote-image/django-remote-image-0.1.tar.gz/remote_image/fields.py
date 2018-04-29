import copy
import io
import urllib.request

from django.core import validators
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms.fields import ImageField
from django.forms.widgets import URLInput
from django.utils.translation import gettext_lazy as _
from PIL import Image as ImagePIL


class RemoteImageField(ImageField):
    widget = URLInput
    default_error_messages = {
        'not_whitelisted': _(
            "The format of this file is not whitelisted."
        ),
        'is_blacklisted': _(
            "The format of this file is blacklisted."
        ),        
    }

    def __init__(self, *, ext_whitelist=None, ext_blacklist=None, **kwargs):
        self.ext_whitelist = ext_whitelist
        self.ext_blacklist = ext_blacklist
        super().__init__(**kwargs)

    def to_python(self, url):
        data = self.get_remote_image_as_InMemoryUploadedFile(url)
        return super().to_python(data)

    def get_remote_image_as_InMemoryUploadedFile(self, url):
        image_bytesio = self.download_and_return_BytesIO(url)
        return self.BytesIO_to_InMemoryUploadedFile(image_bytesio)

    def download_and_return_BytesIO(self, url):
        response = urllib.request.urlopen(url)
        img_bytes = response.read()
        img_bytesio = io.BytesIO(img_bytes)
        return img_bytesio

    def BytesIO_to_InMemoryUploadedFile(self, img_bytesio):
        img_length = img_bytesio.getbuffer().nbytes
        img_format = self.BytesIO_to_PIL(img_bytesio).format.lower()
        img_name = "tempfile." + img_format
        img_content_type = "image/" + img_format

        if self.ext_whitelist != None and img_format not in self.ext_whitelist:
            raise ValidationError(
                self.error_messages['not_whitelisted'],
                code='not_whitelisted',
            )
        
        if self.ext_blacklist != None and img_format in self.ext_blacklist:
            raise ValidationError(
                self.error_messages['is_blacklisted'],
                code='is_blacklisted',
            )
        
        return InMemoryUploadedFile(
                img_bytesio,
                field_name='tempfile',
                name=img_name,
                content_type=img_content_type,
                size=img_length,
                charset='utf-8',
            )

    def BytesIO_to_PIL(self, img_bytesio):
        img_copy = copy.copy(img_bytesio)
        return ImagePIL.open(img_copy)
