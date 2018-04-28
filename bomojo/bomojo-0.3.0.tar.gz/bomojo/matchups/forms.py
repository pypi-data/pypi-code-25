# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import ModelForm

from bomojo.matchups.models import Matchup


class MatchupForm(ModelForm):
    class Meta:
        model = Matchup
        fields = ['title', 'description', 'movies', 'period']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.user = request.user
