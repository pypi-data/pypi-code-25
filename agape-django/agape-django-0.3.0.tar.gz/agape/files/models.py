from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class File (models.Model):

    entity = 'file'
    
    progenitor  = models.CharField(max_length=64 ,null=True, blank=True)

    name         = models.CharField(max_length=255,null=True ,blank=True)
    type         = models.CharField(max_length=16 ,null=True ,blank=True)
    path         = models.TextField(max_length=255, null=True, blank=True)

    label        = models.CharField(max_length=255 ,null=True ,blank=True)
    description  = models.TextField(null=True,blank=True)

    uploaded     = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    uploaded_by  = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name="uploaded_user")

    def moniker(self):
        return '{}:{}'.format(self.entity, self.id)

    def __str__(self):
        return '<{} {} {}>'.format(self.moniker(), self.type, self.value)

