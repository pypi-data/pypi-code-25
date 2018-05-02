# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.forms import ModelForm

from bomojo.backends import get_user_backend
from bomojo.matchups.models import Matchup


class MatchupForm(ModelForm):
    class Meta:
        model = Matchup
        fields = ['title', 'description', 'movies', 'period', 'featured']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.user = request.user

    def clean_featured(self):
        if self.cleaned_data['featured']:
            user_backend = get_user_backend()
            if not user_backend.is_featured_contributor(self.instance.user):
                raise ValidationError('You must be a featured contributor to '
                                      'create featured matchups.',
                                      code='not_featured_contributor')
        return self.cleaned_data['featured']
