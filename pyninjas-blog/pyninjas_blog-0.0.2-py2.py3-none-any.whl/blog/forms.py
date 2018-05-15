from django.utils.translation import ugettext_lazy as _
from django import forms
from .models import Post
from .widgets import html_widget


class PostForm(forms.ModelForm):
    article = forms.CharField(
        label=_("Article"),
        widget=html_widget()(attrs={'cols': 200, 'rows': 30})
    )

    class Meta:
        model = Post
        # fields = ['title', 'slug', 'featured_image', 'article', 'author', 'tags', ]
        fields = '__all__'
