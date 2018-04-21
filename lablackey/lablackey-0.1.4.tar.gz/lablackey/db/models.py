from django.conf import settings
from django.contrib.sessions.models import Session
from django.db import models
from django.http import HttpRequest
from django.template.defaultfilters import slugify

from annoying.fields import AutoOneToOneField

def as_json(self):
  out = {}
  if not getattr(self,"_private_id",None) and not 'pk' in self.json_fields:
    out['id'] = self.id
  for f in self.json_fields:
    key = f
    if type(f) == tuple:
      f, key = f
    out[key] = getattr(self,f)
  for f in self.fk_json_fields:
    if getattr(self,f):
      out[f] = getattr(self,f).as_json
  for f in self.m2m_json_fields:
    out[f] = [i .as_json for i in getattr(self,f)]
  #! TODO: not 100% sure we need this
  out['app_label'] = self._meta.app_label
  out['model_name'] = self._meta.model_name
  return out

def lite_json(self):
  out = { 'id': self.id, 'title': self.__unicode__() }
  if hasattr(self,'get_absolute_url'):
    out['url'] = self.get_absolute_url()
  if hasattr(self,'ur_admin'):
    out['ur_admin'] = self.ur_admin
  for attr in getattr(self,'lite_fields',[]):
    out[attr] = getattr(self,attr)
  return out

def register(model,**kwargs):
  kwargs2 = dict(
    table_permissions = False,
    row_permissions = False,
    filter_fields = [],
    json_fields = [],
    as_json = property(as_json),
    lite_json = property(lite_json),
    fk_json_fields = [],
    m2m_json_fields = [],
  )
  kwargs2.update(kwargs)
  kwargs = kwargs2
  for key,value in kwargs.items():
    if not getattr(model,key,None):
      setattr(model,key,value)
  if not model().json_fields:
    for field in model._meta.get_fields():
      if isinstance(field,models.ManyToOneRel):
        continue
      if isinstance(field,models.ManyToManyField):
        continue
      if isinstance(field,models.ForeignKey):
        model.json_fields.append(field.attname)
      else:
        model.json_fields.append(field.name)

class JsonMixin(object):
  json_fields = ['pk']
  filter_fields = []
  m2m_json_fields = []
  fk_json_fields = []
  _private_id = False
  table_permissions = classmethod(lambda clss,user: True)
  row_permissions = lambda self,user: True
  # Row permissions and table permissions should be implemented as a classmethod and method. Like this
  """
  @classmethod
  def table_permissions(cls,user): # whether or not user can view table (class)
    return True
  def row_permissions(self,user): # whether or not user can view row (instance)
    return True
  """
  lite_json = property(lite_json)
  as_json = property(as_json)
  get_api_kwargs = classmethod(lambda cls,request: ([],{}))

class JsonModel(models.Model,JsonMixin):
  created = models.DateTimeField(auto_now_add=True)
  modified = models.DateTimeField(auto_now=True)
  class Meta:
    abstract = True

class NamedModel(JsonModel):
  name = models.CharField(max_length=128)
  __unicode__ = lambda self: self.name
  class Meta:
    abstract = True

def _prep_with_auth(*args,**kwargs):
  request = kwargs.pop("request",None)
  if args and issubclass(args[0].__class__,HttpRequest):
    request = args[0]
    args = args[1:]
  if not request:
    return args,kwargs
  if request.user.is_authenticated():
    kwargs['user'] = request.user
  else:
    if not request.session.exists(request.session.session_key):
      request.session.create()
    kwargs['session'] = Session.objects.get(session_key=request.session.session_key)
  return args,kwargs

class UserOrSessionManager(models.Manager):
  def get(self,*args,**kwargs):
    try:
      return self.request_filter(*args,**kwargs)[0]
    except IndexError,e:
      raise self.model.DoesNotExist(e)
  def get_or_init(self,*args,**kwargs):
    try:
      return self.get(*args,**kwargs),False
    except self.model.DoesNotExist:
      pass

    # need session or user
    args,kwargs = _prep_with_auth(*args,**kwargs)
    defaults = kwargs.pop("defaults",{})

    #can't make an object with an id, pk, or complex lookup
    kwargs.pop("id","")
    kwargs.pop("pk","")
    for key in kwargs.items():
      if "__" in key:
        kwargs.pop(key,"")

    obj = self.model(**kwargs)
    for k,v in defaults.items():
      setattr(obj,k,v)
    return obj, True

  def get_or_create(self,*args,**kwargs):
    obj,new = self.get_or_init(*args,**kwargs)
    if new:
      obj.save()
    return obj, new

  def request_filter(self,*args,**kwargs):
    args,kwargs = _prep_with_auth(*args,**kwargs)
    return self.filter(*args,**kwargs)

class UserOrSessionModel(JsonModel):
  user = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,related_name="user_%(app_label)s%(class)ss")
  session = models.ForeignKey(Session,null=True,blank=True,related_name="user_%(app_label)s%(class)ss",
                              on_delete=models.SET_NULL)
  session_key = models.CharField(max_length=40,null=True,blank=True)
  objects = UserOrSessionManager()
  filter_fields = ['user_id']
  can_edit_own = False
  private = False
  def row_permissions(self,user):
    if user.is_superuser or (self.user and self.user == user):
      return True
    if self.session and (self.session == user):
      return True
  class Meta:
    abstract = True

class OrderedModel(models.Model):
  order = models.PositiveIntegerField(default=99999)
  def save(self,*args,**kwargs):
    if self.order == 99999:
      self.order = 0
      if self.__class__.objects.count():
        self.order = self.__class__.objects.order_by("-order")[0].order+1
    super(OrderedModel,self).save(*args,**kwargs)
  class Meta:
    abstract = True

def to_base32(s):
  key = '-abcdefghijklmnopqrstuvwxyz'
  s = s.strip('0987654321')
  return int("0x"+"".join([hex(key.find(i))[2:].zfill(2) for i in (slugify(s)+"----")[:4]]),16)

class NamedTreeModel(models.Model):
  name = models.CharField(max_length=64)
  parent = models.ForeignKey("self",null=True,blank=True)
  order = models.FloatField(default=0)
  level = models.IntegerField(default=0)
  def get_order(self):
    if self.parent:
      self.level = self.parent.level + 1
      return to_base32(self.parent.name) + to_base32(self.name)/float(to_base32("zzzz"))
    self.level = 0
    return to_base32(self.name)
  def save(self,*args,**kwargs):
    self.order = self.get_order()
    super(NamedTreeModel,self).save(*args,**kwargs)

  __unicode__ = lambda self: "(%s) %s"%(self.parent,self.name) if self.parent else self.name
  class Meta:
    abstract = True

class SlugModel(models.Model):
  title = models.CharField(max_length=128)
  __unicode__ = lambda self: self.title
  slug = models.CharField(max_length=128,null=True,blank=True,unique=True)
  def save(self,*args,**kwargs):
    self.slug = slugify(self.title)
    if self.__class__.objects.filter(slug=self.slug).exclude(id=self.id):
      self.slug += "-%s"%self.id
    return super(SlugModel,self).save(*args,**kwargs)
  class Meta:
    abstract = True

class UserModel(JsonModel):
  user = models.ForeignKey(settings.AUTH_USER_MODEL)
  can_edit_own = False
  private = False
  def row_permissions(self,user):
    return getattr(self,'public',None) or user.is_superuser or (user == self.user)
  class Meta:
    abstract = True

class User121Model(JsonModel):
  user = AutoOneToOneField(settings.AUTH_USER_MODEL)
  can_edit_own = False
  private = False
  def row_permissions(self,user):
    return getattr(self,'public',None) or user.is_superuser or (user == self.user)
  class Meta:
    abstract = True
  class Meta:
    abstract = True
