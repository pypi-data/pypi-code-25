from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
import string

# Create your models here.

DIGIT_CHARS = set(string.digits)

def numberthing_validate(value, length):
    if (set(value) - DIGIT_CHARS):
        raise ValidationError(
            _('%(value)s is not a number: it contains non-digit characters'),
            params={'value': value},
        )
    if (len(value) != length):
        raise ValidationError(
            _('Incorrect entry %(value)s: it is not exactly %(length)s digits long'), params={'value': value, 'length':length}
        )

def phonenumber_validate(value):
    numberthing_validate(value, 8)

CHOICES_SEXO = (
    ('m', _('Male')),
    ('f', _('Famale'))
)

CHOICES_CURSUS = (
    (1, 'English Basic'),
    (2, 'Pre-Intermediario'),
    (3, 'Microsoft Word'),
    (4, 'Microsoft Excel'),
    (5, 'Microsoft Power-Point'),
    (6, 'Microsoft Access'),
    (7, 'Microsoft Publisher'),
    (8, 'Linguage Portugues-I'),
    (9, 'Linguage Portugues-II'),
)

class RegistuKursu(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birthday = models.DateField()
    place = models.CharField(max_length=30)
    phonenumber = models.CharField(max_length=8, null=True, blank=True, validators=[phonenumber_validate], unique=True)
    sexo = models.CharField(max_length=1, choices=CHOICES_SEXO)
    cursu = models.IntegerField(choices=CHOICES_CURSUS)
