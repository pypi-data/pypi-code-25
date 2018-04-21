import os, re, datetime, random
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.defaultfilters import slugify, striptags
from django.utils import timezone

from tagging.registry import register as tagging_register

from .templatetags.short_codes import explosivo
from lablackey.db.models import UserModel
from lablackey.decorators import cached_property
from media.models import Photo, PhotosMixin
from lablackey.db.models import OrderedModel

from jsonfield import JSONField

TEMPLATE_CHOICES = getattr(settings,"POST_TEMPLATE_CHOICES",['default'])

TEMPLATE_CHOICES = [(t,t) if (not type(t) in [list,tuple]) else t for t in TEMPLATE_CHOICES]
POST_TYPES = [
  ['blog','blog'],
  ['flatpage','flatpage'],
]

class Post(PhotosMixin,UserModel):
  public = True
  user_can_edit = True
  STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('published', 'Published'),
  )

  title = models.CharField(max_length=200, blank=True)
  subtitle = models.CharField(max_length=200, blank=True,null=True)
  _slug = models.CharField(max_length=200,null=True,blank=True)
  slug = property(lambda self: slugify(self._slug or self.title))
  content = models.TextField(blank=True)
  _ht = "A short description to show in front page feed."
  short_content = models.TextField(null=True,blank=True,help_text=_ht)
  get_short_content = lambda self: striptags(explosivo(self.short_content or self.content))
  status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=0)
  template = models.CharField(max_length=64,choices=TEMPLATE_CHOICES,default=TEMPLATE_CHOICES[0][0])
  post_type = models.CharField(max_length=64,choices=POST_TYPES,default=POST_TYPES[0][0])
  extra = JSONField(default=dict,blank=True)
  _ht = "Only used for type flatpage. Url should start and end with \"/\""
  url = models.CharField(max_length=200,blank=True,null=True,help_text=_ht)
  publish_dt = models.DateTimeField("Publish On",null=True,default=timezone.now)
  create_dt = models.DateTimeField(auto_now_add=True)
  update_dt = models.DateTimeField(auto_now=True)
  _h = "Featured blogs must have a photo or they won't appear at all."
  featured = models.BooleanField(default=False,help_text=_h)
  photo = models.ForeignKey(Photo,null=True,blank=True)
  description = property(lambda self: explosivo(self.content))
  lite_fields = ['title', 'photo_url', 'id', 'publish_dt', 'extra']
  json_fields = ['title','template','content','short_content','publish_dt','post_type','subtitle','extra','photo_url']
  photo_url = property(lambda self: self.first_photo.file.url if self.first_photo else None)
  objects = models.Manager()

  @cached_property
  def first_photo(self):
    return self.photo or super(Post,self).first_photo

  class Meta:
    ordering = ('-featured','-publish_dt',)
  __unicode__ = lambda self: self.title or 'Untitled'

  def save(self, *args, **kwargs):
    self._slug = slugify(self._slug or "")
    super(Post, self).save(*args, **kwargs)

  @property
  def META(self):
    image = self.first_photo.file.url if self.first_photo else None
    if image:
      image = settings.SITE_URL + image
    return {
      'description': self.get_short_content(),
      'title': unicode(self),
      'image': image,
    }
  #depracate please
  list_users = property(lambda self: [self.user])

  ur_admin = property(lambda self: "/forms/blog.PostForm/%s/"%self.pk)
  get_absolute_url = lambda self: self.url or reverse("post_detail", args=[self.id, self.slug])
  @classmethod
  def get_api_kwargs(cls,request):
    q = models.Q(status='published',publish_dt__lte=timezone.now())
    if request.user.is_authenticated():
      q = models.Q(status='published',publish_dt__lte=timezone.now()) | models.Q(user=request.user)
      if request.user.is_superuser:
        q = models.Q()
    return [q],{}
tagging_register(Post)

class PressItem(models.Model):
  title = models.CharField(max_length=64)
  url = models.URLField(max_length=256)
  publish_dt = models.DateField("Date")
  __unicode__ = lambda self: self.title
  class Meta:
    ordering = ('-publish_dt',)

WEIGHT_CHOICES = zip(range(1,6),range(1,6))

class BannerManager(models.Manager):
  def get_random(self,*args,**kwargs):
    today = datetime.date.today()
    banners = self.filter(start_date__lte=today,end_date__gte=today,active=True)
    if not banners:
      return
    choices = []
    for i,banner in enumerate(banners):
      choices += [i]*banner.weight
    return banners[random.choice(choices)]

class Banner(models.Model):
  start_date = models.DateField(default=datetime.date.today)
  end_date = models.DateField(blank=True)
  name = models.CharField(max_length=64)
  header = models.CharField(default="Featured Event",max_length=32,null=True,blank=True)
  active = models.BooleanField(default=True)
  src = models.ImageField(upload_to="banners")
  url = models.CharField(max_length=200)
  weight = models.IntegerField(choices=WEIGHT_CHOICES)
  objects = BannerManager()
  __unicode__ = lambda self: self.name
  def save(self,*args,**kwargs):
    self.end_date = self.end_date or datetime.date(2099,1,1)
    super(Banner,self).save(*args,**kwargs)
  class Meta:
    ordering = ('name',)
