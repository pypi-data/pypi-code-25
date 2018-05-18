from django.db import models


class MoneyObjectsManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(*self.model.get_money_field_names())
