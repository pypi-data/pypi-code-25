# -*- coding: utf-8 -*-
__all__ = ['ConstrainedImageField']

import os

from django import forms
from django.conf import settings
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


class ConstrainedImageField(models.ImageField):
    """
    An ImageField with additional constraints. Namely, the file size and type can be restricted. If
    using the types, the magic library is required. Setting neither a file size nor type behaves
    like a regular FileField.

    Parameters
    ----------
    content_types : list of str
        List containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
    [min|max]_upload_size : int
        Maximum file size allowed for upload, in bytes
            1 MB - 1048576 B - 1024**2 B - 2**20 B
            2.5 MB - 2621440 B
            5 MB - 5242880 B
            10 MB - 10485760 B
            20 MB - 20971520 B
            33 MiB - 2**25 B
            50 MB - 5242880 B
            100 MB 104857600 B
            250 MB - 214958080 B
            500 MB - 429916160 B
            1 GiB - 1024 MiB - 2**30 B
    [min|max]_upload_[heigth|width] : int
    js_checker : bool
        Add a javascript file size checker to the form field
    mime_lookup_length : int

    See Also
    --------
    Based on https://github.com/kaleidos/django-validated-file/blob/master/validatedfile/fields.py
    With inspiration from http://stackoverflow.com/a/9016664

    """

    description = _("An image file field with constraints on size and/or type")

    _constraint_prefix = 'upload_'
    _constrained_fields = ['size', 'height', 'width']

    @property
    def _constraints(self):
        return {field: self._constraint_prefix + field for field in self._constrained_fields}

    def __init__(self, *args, **kwargs):
        for attribute in self._constraints.values():
            setattr(self, attribute, {})
            for boundary in ['min', 'max']:
                value = kwargs.pop(boundary + "_" + attribute, 0)
                assert isinstance(value, int) and value >= 0
                getattr(self, attribute)[boundary] = value
        self.content_types = kwargs.pop("content_types", [])
        self.mime_lookup_length = kwargs.pop("mime_lookup_length", 4096)
        assert isinstance(self.mime_lookup_length, int) and self.mime_lookup_length >= 0
        self.js_checker = kwargs.pop("js_checker", False)

        super(ConstrainedImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ConstrainedImageField, self).clean(*args, **kwargs)
        errors = []

        for field in self._constrained_fields:
            attribute = getattr(self, self._constraints[field])
            below = attribute['min'] and getattr(data, field) < attribute['min']
            above = attribute['max'] and getattr(data, field) > attribute['max']
            if below or above:
                # Ensure no one bypasses the js checker
                errors.append(
                    _('File %(field)s ' + (
                        'below' if below else 'exceeds') + ' limit: %(current_size)s. Limit is %(limit)s.') %
                    {'field': field,
                     'limit': filesizeformat(attribute['min' if below else 'max']) if field == 'size' else
                     attribute['min' if below else 'max'],
                     'current_size': filesizeformat(data.size) if field == 'size' else data.size})

        if self.content_types:
            import magic
            file = data.file
            uploaded_content_type = getattr(file, 'content_type', '')

            # magic_file_path used only for Windows.
            magic_file_path = getattr(settings, "MAGIC_FILE_PATH", None)
            if magic_file_path and os.name == 'nt':
                mg = magic.Magic(mime=True, magic_file=magic_file_path)
            else:
                mg = magic.Magic(mime=True)
            content_type_magic = mg.from_buffer(file.read(self.mime_lookup_length))
            file.seek(0)

            # Prefer mime-type from magic over mime-type from http header
            if uploaded_content_type != content_type_magic:
                uploaded_content_type = content_type_magic

            if uploaded_content_type not in self.content_types:
                errors.append(
                    _('Unsupported file type: %(type)s. Allowed types are %(allowed)s.') %
                    {'type': content_type_magic,
                     'allowed': self.content_types})
        if errors:
            raise forms.ValidationError(errors)

        return data

    def formfield(self, **kwargs):
        """
        Usual Form for a django.models.FileField with optional javascript file size
        checker. Can thus be customized as any other Form for a django.models.FileField.

        Parameters
        ----------
        kwargs
            will be passed to super().formfield()

        Returns
        -------
        django.forms.FileField

        """
        formfield = super(ConstrainedImageField, self).formfield(**kwargs)
        if self.js_checker:
            formfield.widget.attrs.update(
                {'onchange': 'validateFileSize(this, %d, %d);' % (
                    getattr(self, self._constraints['size'])['min'], getattr(self, self._constraints['size'])['max'],)})
        return formfield

    def deconstruct(self):
        name, path, args, kwargs = super(ConstrainedImageField, self).deconstruct()
        for attribute in self._constraints.values():
            for boundary in ['min', 'max']:
                value = getattr(self, attribute)[boundary]
                if value:
                    kwargs[boundary + "_" + attribute] = value
        if self.content_types:
            kwargs["content_types"] = self.content_types
        if self.mime_lookup_length:
            kwargs["mime_lookup_length"] = self.mime_lookup_length
        if self.js_checker:
            kwargs["js_checker"] = self.js_checker
        return name, path, args, kwargs

    def __str__(self):
        if hasattr(self, 'model'):
            return super(ConstrainedImageField).__str__()
        else:
            return self.__class__.__name__
