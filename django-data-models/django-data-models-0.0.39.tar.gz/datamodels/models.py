from __future__ import unicode_literals

from django.db import models


class DataModelsReadOnlyException(Exception):
    pass


class DataModelQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        if getattr(self.model.DataModelMeta, 'readonly', False):
            raise DataModelsReadOnlyException("You can't delete DataModel objects with DataModelMeta.readonly==True")
        return super(DataModelQuerySet, self).delete(*args, **kwargs)

    def update(self, *args, **kwargs):
        if getattr(self.model.DataModelMeta, 'readonly', False):
            raise DataModelsReadOnlyException("You can't update DataModel objects")
        return super(DataModelQuerySet, self).update(*args, **kwargs)

    def select_for_update(self, *args, **kwargs):
        if getattr(self.model.DataModelMeta, 'readonly', False):
            raise DataModelsReadOnlyException("You can't update DataModel objects")
        return super(DataModelQuerySet, self).select_for_update()


class DataModel(models.Model):
    objects = DataModelQuerySet.as_manager()

    class DataModelMeta:
        fixtures = []
        default_fixtures = []
        dependencies = []
        readonly = False

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if getattr(self.DataModelMeta, 'readonly', False):
            raise DataModelsReadOnlyException("You can't update or create DataModel objects")
        return super(DataModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if getattr(self.DataModelMeta, 'readonly', False):
            raise DataModelsReadOnlyException("You can't delete DataModel objects")
        return super(DataModel, self).delete(*args, **kwargs)
