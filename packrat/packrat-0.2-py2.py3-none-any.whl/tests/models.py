from django.db import models
from ..storage import PackratStorage

storage = PackratStorage('http://localhost:8000')


class TestModel(models.Model):
    some_file = models.FileField(storage=storage)
