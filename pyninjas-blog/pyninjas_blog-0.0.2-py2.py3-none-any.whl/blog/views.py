from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from .models import Post, Tag, Comment


def index(request, tag=None):
    if tag:
        try:
            _tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            raise Http404(_(f"Tag {tag} not found."))
        qs = _tag.articles.all()
    else:
        qs = Post.objects.all()
        _tag = None
    if not request.user.is_staff:
        qs.filter(is_draft=False)
    # Paginate
    paginator = Paginator(qs, settings.PAGINATION_LIMIT)
    page = request.GET.get('page', 1)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/index.html', {'posts': posts, 'tag': _tag})


def article(request, slug):
    try:
        post = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        raise Http404(_(f"Article {slug} not found."))
    return render(request, 'blog/article.html', {'post': post})
