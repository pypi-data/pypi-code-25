from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django import forms
from django.shortcuts import get_object_or_404

class UserEmailForm(forms.ModelForm):
  class Meta:
    fields = ('email',)
    model = get_user_model()

class RequestModelForm(forms.ModelForm):
  """
  Just like a normal form but requires a request as the first argument rather than data.
  Takes GET/POST and FILES from request, so you should NOT pass these in.
  Attaches request to form for later use.

  example_form = RequestModelForm(request,initial={'city':'Houston'})
  user = example_form.request.user
  """
  is_user_form = False
  @property
  def ur_admin(self):
    return reverse(args=[self.__module__.replace(".forms","")])
  def __init__(self,request,*args,**kwargs):
    self.request = request
    super(RequestModelForm,self).__init__(self.request.POST or None,self.request.FILES or None,*args,**kwargs)
  def save(self,*args,**kwargs):
    commit = kwargs.pop("commit",True)
    kwargs['commit'] = False
    super(RequestModelForm,self).save(*args,**kwargs)
    if self.is_user_form and not self.instance.user:
      self.instance.user = self.request.user
    if commit:
      self.instance.save()
    return self.instance
  @classmethod
  def user_is_allowed(clss,request):
    return request.user.is_authenticated() and request.user.is_superuser
  @classmethod
  def get_list_fields(clss,obj):
    return [
      unicode(obj),
    ]
  @classmethod
  def get_instance(clss,request,id=None):
    if not id:
      return
    return get_object_or_404(clss.Meta.model,id=id)
  @classmethod
  def get_page_json(clss,page=0):
    per_page = 100
    start = int(page)*per_page
    end = start + per_page
    results = []
    for obj in clss.Meta.model.objects.all()[start:end]:
      out = {
        'id': obj.id,
        'url': getattr(obj,'get_absolute_url',lambda: None)(),
        'ur_admin': getattr(obj,'ur_admin',None),
        'fields': clss.get_list_fields(obj)
      }
      results.append(out)
    return dict(
      page=page,
      results=results,
    )

class RequestForm(forms.Form):
  """ Same as above but inherits from Form instead of ModelForm"""
  def __init__(self,request,*args,**kwargs):
    self.request = request
    super(RequestForm,self).__init__(self.request.POST or None,self.request.FILES or None,*args,**kwargs)
