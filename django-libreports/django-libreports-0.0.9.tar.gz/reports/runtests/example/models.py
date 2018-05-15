from django.db import models


class Organization(models.Model):
    """
    Customer's Organization Model
    """

    name = models.CharField(unique=True, max_length=1024)
