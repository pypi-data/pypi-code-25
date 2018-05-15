from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth import get_user_model
from os import path as ospath
import logging


logger = logging.getLogger(__name__)


def featured_upload_path(instance, filename):
    logger.debug("Uploading file {name} as featured image for {post}".format(
        name=filename, post=instance.slug
    ))
    return ospath.join('blog', str(instance.slug), filename)


class Tag(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"))

    @property
    def size(self):
        return self.articles.count()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Post(models.Model):
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(_("Slug"))
    featured_image = models.ImageField(_("Featured Image"), upload_to=featured_upload_path, blank=True, null=True)
    article = models.TextField(_("Article"))
    author = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='articles',
        verbose_name=_("Author")
    )
    tags = models.ManyToManyField(Tag, related_name='articles')
    is_draft = models.BooleanField(_("Draft"), default=True)
    allow_comments = models.BooleanField(_("Allow Comments"), default=True)
    # Metas
    meta_description = models.CharField(_("Meta Description"), max_length=255, null=True, blank=True)
    meta_keywords = models.CharField(_("Meta Keywords"), max_length=160, null=True, blank=True)
    published_at = models.DateTimeField(_("Publish Date"), null=True, blank=True)
    # Stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.published_at and not self.is_draft:
            self.published_at = self.updated_at
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-published_at',)
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")


class Comment(models.Model):
    article = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments',
        verbose_name=_("Article")
    )
    comment = models.TextField(_("Comment"))
    author = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='comments',
        verbose_name=_("Author")
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='children',
        verbose_name=_("Parent Comment"), null=True, blank=True
    )
    disabled = models.BooleanField(_("Disabled"), default=False)
    # Stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
