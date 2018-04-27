# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin

from adminsortable.admin import SortableAdmin
from glitter import block_admin
from glitter.admin import GlitterAdminMixin, GlitterPagePublishedFilter

from .models import Category, LatestNewsBlock, Post


@admin.register(Category)
class CategoryAdmin(SortableAdmin):
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Post)
class PostAdmin(GlitterAdminMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('title', 'date', 'category', 'is_published', 'is_sticky')
    list_filter = (GlitterPagePublishedFilter, 'date', 'category')
    prepopulated_fields = {'slug': ('title',)}

    def get_fieldsets(self, request, obj=None):
        advanced_options = ['is_sticky', 'slug']

        if getattr(settings, 'GLITTER_NEWS_TAGS', False):
            advanced_options.append('tags')

        fieldsets = ((
            'Post',
            {'fields': ('title', 'category', 'author', 'date', 'image', 'summary', 'tags')}
        ), ('Advanced options', {'fields': advanced_options}),)
        return fieldsets


block_admin.site.register(LatestNewsBlock)
block_admin.site.register_block(LatestNewsBlock, 'App Blocks')
