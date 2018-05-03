from django.db import models

from constrainedfilefield.fields import ConstrainedFileField, ConstrainedImageField


class TestModel(models.Model):
    the_file = ConstrainedFileField(
        null=True,
        blank=True,
        upload_to='testfile',
        content_types=['image/png'],
        max_upload_size=10240)


class TestImageModel(models.Model):
    the_image = ConstrainedImageField(
        null=True,
        blank=True,
        upload_to='testfile', )
    the_image_small = ConstrainedImageField(
        null=True,
        blank=True,
        upload_to='testfile',
        content_types=['image/png'],
        min_upload_size=1024,
        max_upload_size=10240,
        min_upload_height=100,
        max_upload_height=500,
        min_upload_width=100,
        max_upload_width=500)
    the_image_large = ConstrainedImageField(
        null=True,
        blank=True,
        upload_to='testfile',
        content_types=['image/png'],
        min_upload_size=10240,
        max_upload_size=20480,
        min_upload_height=3000,
        max_upload_height=5000,
        min_upload_width=3000,
        max_upload_width=5000)


class TestModelJs(models.Model):
    the_file = ConstrainedFileField(
        null=True,
        blank=True,
        upload_to='testfile',
        content_types=['image/png'],
        max_upload_size=10240,
        js_checker=True)
    the_image = ConstrainedImageField(
        null=True,
        blank=True,
        upload_to='testfile',
        content_types=['image/png'],
        min_upload_size=1024,
        max_upload_size=10240,
        js_checker=True)


class TestModelNoValidate(models.Model):
    the_file = ConstrainedFileField(
        null=True,
        blank=True,
        upload_to='testfile')
    the_image = ConstrainedImageField(
        null=True,
        blank=True,
        upload_to='testfile')


class TestContainer(models.Model):
    name = models.CharField(max_length=100)


class TestElement(models.Model):
    container = models.ForeignKey(
        TestContainer,
        on_delete=models.CASCADE,
        related_name='test_elements')
    the_file = ConstrainedFileField(
        null=True,
        blank=True,
        upload_to='testfile',
        content_types=['image/png', 'image/jpeg'])
