from django.db import models

# Create your models here.

class Parameter (models.Model):
    ''' 
        List of parameters changable in Admin used within the project 
        These parameters are added through manage.py initialise and cannot be created or deleted in admin, only updated
    '''

    name = models.CharField (
        verbose_name = 'Title',
        max_length = 30,
        primary_key=True 
    )
    text = models.TextField (
        verbose_name = 'Text String to be used',
    )
    f = models.FileField (
        upload_to = 'paramaters/',
        blank=True,
        null=True,
        verbose_name = "File",
        help_text = 'Add a file if required for parameter'
    )

    def __str__(self):
        return u'%s' % (self.name)