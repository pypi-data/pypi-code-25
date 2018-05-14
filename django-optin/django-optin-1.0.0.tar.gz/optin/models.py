from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from optin.utils import USER_MODEL
# Create your models here.

BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

class Category (models.Model):
    ''' Model describing the different things that the user can opt in or out of
    '''
    title = models.CharField (
        verbose_name = 'Title',
        max_length = 255
    )
    description = models.TextField(
        verbose_name = 'Description',
        help_text = 'Description displayed to user of the usage of this Category'
    )
    default = models.BooleanField(
        verbose_name = 'Default',
        default = False,
        help_text = 'Default used for new User Preference',
        choices=BOOL_CHOICES
    )

    def __str__(self):
        return self.title

class UserOptin (models.Model):
    ''' Model describing the user selection for each Category
    '''
    user = models.ForeignKey(
        USER_MODEL, 
        related_name='optin',
        on_delete=models.CASCADE
    )
    category = models.ForeignKey (
        Category,
        on_delete=models.CASCADE
    )
    option = models.NullBooleanField(
        verbose_name = 'User Preference',
        null = True,
        blank = True,
        help_text = 'Select to opt in',
        choices=BOOL_CHOICES
    )

    class Meta:
        unique_together =['user','category']

    def __str__(self):
        return str(self.user) + ' ' + str(self.category)

    def save(self, *args, **kwargs):
        if not self.option:
            self.option = self.category.default
        super(UserOptin, self).save(*args, **kwargs)