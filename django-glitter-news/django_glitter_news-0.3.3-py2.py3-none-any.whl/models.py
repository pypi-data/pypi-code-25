# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from adminsortable.models import SortableMixin
from glitter.assets.fields import AssetForeignKey
from glitter.mixins import GlitterMixin
from glitter.models import BaseBlock
from taggit.managers import TaggableManager


@python_2_unicode_compatible
class Category(SortableMixin):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('order',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('glitter-news:post-list-category', args=(self.slug,))


@python_2_unicode_compatible
class Post(GlitterMixin):
    title = models.CharField(max_length=100, db_index=True)
    category = models.ForeignKey('glitter_news.Category')
    is_sticky = models.BooleanField(default=False)
    author = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=100, unique_for_date='date')
    date = models.DateTimeField(default=timezone.now, db_index=True)
    # Is in used in overriding get_absolute_url method in case externals apps needs different URL.
    url = models.URLField(blank=True, editable=False)
    image = AssetForeignKey('glitter_assets.Image', null=True, blank=True)
    summary = models.TextField(blank=True)

    tags = TaggableManager(blank=True)

    class Meta(GlitterMixin.Meta):
        get_latest_by = 'date'
        ordering = ('-is_sticky', '-date',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """ Get absolute url sometimes we assign external url to the post. """
        url = '/'
        if self.url:
            url = self.url
        else:
            publication_date = self.date
            if timezone.is_aware(publication_date):
                publication_date = timezone.localtime(publication_date)
            params = {
                'year': publication_date.strftime('%Y'),
                'month': publication_date.strftime('%m'),
                'day': publication_date.strftime('%d'),
                'slug': self.slug,
            }
            url = reverse('glitter-news:post-detail', kwargs=params)
        return url


class LatestNewsBlock(BaseBlock):
    category = models.ForeignKey('glitter_news.Category', null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'latest news'
