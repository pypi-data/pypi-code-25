import itertools

from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from ckeditor_uploader.fields import RichTextUploadingField

from blog.utils import USER_MODEL
# Create your models here.

class Tag (models.Model):
    name = models.CharField(
        verbose_name = 'Tag',
        max_length = 30,
    )
    
    def __str__(self):
        return u'%s' % (self.name)    


class BlogQuerySet(models.QuerySet):
    def live_blogs(self, yag):
        query = models.Q(live=True)
        if tag != None: query = query & models.Q(tag=tag)
        return self.filter(query)

    def text_search(self, query):
        query = models.Q(live=True) & models.Q(query)
        return self.filter(query)

class BlogManager(models.Manager):
    def get_queryset(self):
        return BlogQuerySet(self.model, using=self._db)  

    def live_blogs(self, tag=None):
        return self.get_queryset().live_listings(tag)

    def text_search(self, query=None):
        return self.get_queryset().text_search(query)

class Blog (models.Model):
    name = models.CharField (
        verbose_name = "Title",
        max_length = 80,
    )
    short_description = models.TextField()
    blog = RichTextUploadingField ()
    image = models.ImageField (
        verbose_name = "Main Image",
        upload_to ="blog_main_image/"
    )
    date = models.DateField(
        default = timezone.now
    )
    author = models.ForeignKey(
        USER_MODEL,
        verbose_name = "Author",
        on_delete=models.CASCADE
    )
    tag = models.ManyToManyField(
        Tag
    )
    slug = models.SlugField(
        verbose_name = 'Slug',
        allow_unicode = True,
        unique = True,
        blank = True,
        null = True
    )
    live = models.BooleanField(
        default = True
    )

    objects = BlogManager()
    
    def __str__(self):
        return u'%s' % (self.name)
    
    class Meta:
        ordering = ['-date']
    
    @models.permalink
    def get_absolute_url(self):
        return ('blog:blog-detail', (), {'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        
        orig = self.slug
        if not Blog.objects.filter(slug=self.slug).exists():
            pass
        else:
            b = Blog.objects.get(slug=self.slug)
            if b == self: pass
            else :
                for x in itertools.count(1):
                    if not Blog.objects.filter(slug=self.slug).exists():
                        break
                    self.slug = '%s-%d' % (orig, x)

        super(Blog, self).save(*args, **kwargs)