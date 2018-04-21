# This file should eventually become it's own unrest library, but then again all of lablackey might go that way

from django.db import models
from django import forms

from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder

class LazyEncoder(DjangoJSONEncoder):
  def default(self, obj):
    if isinstance(obj, Promise):
      return force_text(obj)
    return super(LazyEncoder, self).default(obj)

EXCLUDE_FIELDS = ['django.db.models.AutoField']

FIELD_MAP = {
  'django.db.models.CharField': { },
  'django_countries.fields.CountryField': { },
}

TYPES_MAP = [
  (forms.widgets.HiddenInput, "hidden"),
  (forms.widgets.RadioSelect, 'radio'),
  (forms.widgets.CheckboxInput, 'checkbox'),
  (forms.PasswordInput, 'password'),
  (forms.Textarea, 'textarea'),
]
def form_to_schema(form):
  schema = []
  initial = form.initial
  instance = getattr(form,'instance',None)
  if instance and instance.pk:
    initial = instance.as_json
    initial.update(getattr(form,'as_json',{}))
  field_overrides = getattr(form,'field_overrides',{})
  model = hasattr(form,"Meta") and form.Meta.model
  for name,field in form.fields.items():
    if instance and not name in initial:
      initial[name] = getattr(instance,name,None)
    json = field.widget.attrs
    json.update({
      'required': field.required,
      'name': name,
      'label': field.label,
      'help_text': field.help_text
    })
    if not 'type' in json:
      for widget,_type in TYPES_MAP:
        if isinstance(field.widget,widget):
          json['type'] = _type
    if not json['help_text'] and model and name in model._meta.fields:
      json['help_text'] = model._meta.get_field(name).help_text
    if hasattr(field,'choices'):
      json['choices'] = [c for c in field.choices]
    if name in field_overrides:
      json['type'] = field_overrides[name]
    if not json.get('type',None) and json.get('choices',None):
      json['type'] = 'select'
    schema.append(json)
  out = {
    'form_title': getattr(form,"form_title",None),
    'schema': schema,
    'initial': initial,
    'errors': { k: e.get_json_data()[0]['message'] for k,e in form.errors.items() } or None,
    'html_errors': getattr(form,"html_errors",[]),
    'rendered_content': getattr(form,"rendered_content",None),
    'form_title': getattr(form,"form_title",None)
  }
  if hasattr(form,'Media'):
    out['css'] = getattr(form.Media,'css',[])
    out['js'] = getattr(form.Media,'js',[])
  if 'ur_page' in form.request.GET:
    if hasattr(form,'get_page_json'):
      out['ur_pagination'] = form.get_page_json(form.request.GET['ur_page'])
  return out

def model_to_schema(model):
  schema = []
  exclude = getattr(model,"schema_exclude",[])
  for field in model._meta.get_fields():
    if isinstance(field,models.ManyToOneRel):
      continue
    name, path, args, kwargs = field.deconstruct()
    if path in EXCLUDE_FIELDS or name in exclude:
      continue
    json = FIELD_MAP.get(path,{}).copy()
    json['name'] = name
    if kwargs.get('null',False) or kwargs.get('blank',False):
      json['required'] = False
    if kwargs.get("choices",None):
      json['type'] = 'select'
      json['choice_tuples'] = kwargs['choices']
    schema.append(json)
  return schema
