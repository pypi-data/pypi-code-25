from django.apps import apps
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
  
import json

def merge_model(request,app_label,model_name):
  model = apps.get_model(app_label,model_name)
  values = {
    'objects': model.objects.all(),
  } 
  if 'original' in request.GET and 'duplicates' in request.GET:
    fields = [f.name for f in model._meta.get_fields()]
    values['fieldnames'] = fields
    values['original'] = model.objects.filter(id=request.GET['original']).values_list(*fields)[0]
    values['duplicates'] = model.objects.filter(id__in=request.GET.getlist('duplicates')).distinct().values_list(*fields)
  if request.POST:
    for duplicate in duplicates:
      if duplicate.id == original.id:
        messages.error(request,"Can't merge with self! (You selected the same object for keep and merge)")
        continue
      messages.success(request,"Merged and deleted %s"%duplicate)
      for f in original._meta.get_fields():
        if f.one_to_many and f.auto_created:
          getattr(duplicate,f.get_accessor_name()).update(**{f.field.name:original})
      duplicate.delete()
    return HttpResponseRedirect(request.path)
  return TemplateResponse(request,"merge_model.html",values)
