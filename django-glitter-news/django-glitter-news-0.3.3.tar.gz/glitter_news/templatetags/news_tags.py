# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils import timezone

from glitter_news.models import Category, Post
from taggit import utils

register = template.Library()


@register.assignment_tag
def get_news_categories():
    return Category.objects.all()


@register.assignment_tag
def get_news_months():
    return Post.objects.published().filter(date__lte=timezone.now()).dates('date', 'month')


@register.assignment_tag
def get_latest_news(count, category='', tags=''):
    post_list = Post.objects.published().select_related().filter(date__lte=timezone.now())

    # Optional filter by category
    if category.strip():
        post_list = post_list.filter(category__slug=category)

    # Optional filter by tags
    if tags.strip():
        post_list = post_list.filter(tags__name__in=utils.parse_tags(tags))

    return post_list[:count]
