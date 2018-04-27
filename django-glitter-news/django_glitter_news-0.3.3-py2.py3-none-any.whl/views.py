# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import six
from django.views.generic import ArchiveIndexView, DateDetailView

from glitter.mixins import GlitterDetailMixin

from .models import Category, Post


class BasePostListView(ArchiveIndexView):
    allow_empty = True
    date_field = 'date'
    paginate_by = getattr(settings, 'NEWS_PER_PAGE', 10)
    template_name_suffix = '_list'
    context_object_name = 'object_list'
    ordering = ('-is_sticky', '-date', '-id')

    def get_queryset(self):
        queryset = Post.objects.published()

        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, six.string_types):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BasePostListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['news_categories'] = True
        return context


class PostListView(BasePostListView):

    def get_ordering(self):
        if getattr(settings, 'NEWS_STICKY_ON_ALL', True):
            return super().get_ordering()
        else:
            return ('-date', '-id')


class PostListCategoryView(BasePostListView):
    template_name_suffix = '_category_list'

    def get_queryset(self):
        qs = super(PostListCategoryView, self).get_queryset()
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return qs.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super(PostListCategoryView, self).get_context_data(**kwargs)
        context['current_category'] = self.category
        return context


class PostDetailView(GlitterDetailMixin, DateDetailView):
    queryset = Post.objects.select_related().filter(published=True)
    month_format = '%m'
    date_field = 'date'

    def get_allow_future(self):
        """
        Only superusers and users with the permission can edit the post.
        """
        qs = self.get_queryset()
        post_edit_permission = '{}.edit_{}'.format(
            qs.model._meta.app_label, qs.model._meta.model_name
        )
        if self.request.user.has_perm(post_edit_permission):
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        # Add this to display 'All news' on categories list.
        context['news_categories'] = True
        context['current_category'] = self.object.category
        return context


class PostListTagView(PostListView):
    template_name_suffix = '_tag_list'

    def get_queryset(self):
        qs = super(PostListTagView, self).get_queryset()
        self.tag = get_object_or_404(Post.tags.all(), slug=self.kwargs['slug'])
        return qs.filter(tags=self.tag)

    def get_context_data(self, **kwargs):
        context = super(PostListTagView, self).get_context_data(**kwargs)
        context['current_tag'] = self.tag
        return context
