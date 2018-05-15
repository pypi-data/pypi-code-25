from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from .models import Tag, Post, Comment
from .forms import PostForm


class InlineCommentAdmin(admin.TabularInline):
    model = Comment
    fieldsets = (
        ('', {
            'fields': ('comment', 'author', 'parent', 'disabled', 'created_at',)
        }),
    )
    readonly_fields = ('created_at',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name')
    fieldsets = (
        ('', {
            'fields': ('name', 'slug')
        }),
    )
    search_fields = ('slug', 'name')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'author', 'is_draft', 'published_at', 'created_at',)
    list_filter = ('tags', ('author', admin.RelatedOnlyFieldListFilter), 'is_draft', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (_("Post Details"), {
            'fields': ('title', 'slug', 'featured_image', 'author', 'article', 'tags', ('is_draft', 'allow_comments'))
        }),
        (_("META (SEO)"), {
            'fields': ('meta_description', 'meta_keywords', 'published_at')
        }),
        (_("Stamps"), {
            'fields': ('created_at', 'updated_at')
        })
    )
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('title', 'slug')
    inlines = [
        InlineCommentAdmin
    ]
    form = PostForm

