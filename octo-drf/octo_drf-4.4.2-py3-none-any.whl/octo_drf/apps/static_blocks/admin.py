from django import forms
from django.contrib.contenttypes.admin import GenericStackedInline
from django.forms.widgets import Textarea
from sorl.thumbnail.admin import AdminImageMixin

from octo_drf.apps.redactor.widgets import Redactor
from .models import StaticBlock


class StaticBlocForm(forms.ModelForm):

    class Meta:
        widgets = {
            'content': Redactor,
            'announce': Textarea(attrs={'rows': 5, 'cols': 35})
        }


class StaticBlockStackedInline(AdminImageMixin, GenericStackedInline):

    model = StaticBlock
    form = StaticBlocForm
    extra = 0
    fields = ('title', 'content', 'announce',
              'image1', 'image2', 'image3', 'image4',
              'order', 'is_published'
              )