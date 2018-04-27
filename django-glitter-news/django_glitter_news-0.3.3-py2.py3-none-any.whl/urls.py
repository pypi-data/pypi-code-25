# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url

from . import feeds, views

urlpatterns = [
    url(r'^$', views.PostListView.as_view(), name='list'),
    url(
        r'^category/(?P<slug>[-\w]+)/$',
        views.PostListCategoryView.as_view(),
        name='post-list-category'
    ),
    url(
        r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        views.PostDetailView.as_view(),
        name='post-detail'
    ),
    url(r'^feed/$', feeds.NewsFeed(), name='feed'),
    url(r'^feed/(?P<slug>[-\w]+)/$', feeds.NewsCategoryFeed(), name='category-feed'),
]

if getattr(settings, 'GLITTER_NEWS_TAGS', False):
    urlpatterns += [
        url(r'^tag/(?P<slug>[-\w]+)/$', views.PostListTagView.as_view(), name='post-list-tag'),
    ]
