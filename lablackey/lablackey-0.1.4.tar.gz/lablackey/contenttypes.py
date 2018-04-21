from django.db import models
from django.contrib.contenttypes.models import ContentType

import six

class CTCache(object):
  lookup = {}
  def get(self,obj):
    if not isinstance(obj,six.string_types):
      # must be a models.Model
      obj = "%s.%s"%(obj._meta.app_label,obj._meta.model_name)
    obj = obj.lower()
    if obj not in self.lookup:
      self.lookup[obj] = ContentType.objects.get_by_natural_key(*obj.split("."))
    return self.lookup[obj]

get_contenttype = CTCache().get
