from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.exceptions import ObjectDoesNotExist
from django import forms

from .models import Post
from media.models import Photo

import datetime

from lablackey.forms import RequestModelForm
from tagging.forms import TagField
from tagging.models import Tag

class TaggedModelForm(forms.ModelForm):
  """Provides an easy mixin for adding tags using django-tagging"""
  tags = TagField(help_text="Separate tags with commas. Input will be lowercased")
  def __init__(self,*args,**kwargs):
    super(TaggedModelForm,self).__init__(*args,**kwargs)
    instance = kwargs.get('instance',None)
    initial = kwargs.get('initial',{})
    if instance and not initial.get('tags',None):
      self.fields['tags'].initial = ','.join([t.name for t in Tag.objects.get_for_object(instance)])
  def save(self,*args,**kwargs):
    instance = super(TaggedModelForm,self).save(*args,**kwargs)
    if not kwargs.get('commit',True):
      return instance
    Tag.objects.update_tags(instance,self.cleaned_data['tags'])
    return instance
  class Meta:
    abstract = True

class NewPostForm(RequestModelForm):
  field_overrides = {'content': 'simplemde-input'}
  class Media:
    css = {
      'all': ('simplemde/simplemde.min.css',)
    }
    js = ['simplemde/simplemde.min.js']
  class Meta:
    fields = ('title','content','short_content','publish_dt','status','photo')
    model = Post

class PostForm(TaggedModelForm):
  photo = forms.ModelChoiceField(Photo.objects.all(),required=False)
  class Meta:
    model = Post
    fields = ('title', 'tags','photo', 'status','content','short_content')
  class Media:
    css = {
      'all': ('simplemde/simplemde.min.css',)
    }
    js = ['simplemde/simplemde.min.js']

  def save(self,*args,**kwargs):
    try:
      self.instance.user
    except ObjectDoesNotExist:
      self.instance.user = self.user
    return super(PostForm,self).save(*args,**kwargs)

  def __init__(self, *args, **kwargs):
    # checking for user argument here for a more
    self.user = None

    if 'user' in kwargs:
      self.user = kwargs.pop('user', None)
    super(PostForm, self).__init__(*args, **kwargs)
    #self.fields['tags'].help_text = "Separate tags with commas. Input will be lowercased."
    self.fields['photo'].widget=ForeignKeyRawIdWidget(Post._meta.get_field("photo").rel,admin.site)
    # add span class to charfields
    for field in self.fields.values():
      if isinstance(field, forms.fields.CharField):
        if 'class' in field.widget.attrs:
          field.widget.attrs['class'] = "%s %s" % (
            field.widget.attrs['class'],
            'span8',
          )
        else:
          field.widget.attrs['class'] = 'span8'
