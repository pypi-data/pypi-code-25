from django.db import models
from personas.models import Personas


# Create your models here.

class Account(models.Model):
    email = models.EmailField(unique=True)

    class Meta():
        db_table = "accounts"
    def __str__(self):
        return self.email

class Hub(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE, null=True)
    hub_name = models.CharField(max_length=100, default='')
    api_user_name = models.CharField(max_length=255, default='')
    api_password = models.CharField(max_length=255, default='')

    class Meta:
        db_table = 'hubs'
        unique_together = (("account", "hub_name", "api_user_name","api_password"),)
    def __str__(self):
        return self.hub_name

class PersonasToHubs(models.Model):
    personas = models.ForeignKey(Personas, on_delete=models.CASCADE, null=True, blank=True)
    hub = models.ForeignKey('Hub', on_delete=models.CASCADE, null=True)

    class Meta():
        db_table = 'personas_to_hubs'
        verbose_name_plural = 'PersonasToHubs'