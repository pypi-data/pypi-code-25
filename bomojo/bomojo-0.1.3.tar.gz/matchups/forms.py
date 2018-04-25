# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import ModelForm

from matchups.models import Matchup


class MatchupForm(ModelForm):
    class Meta:
        model = Matchup
        fields = ['email', 'title', 'description', 'movies', 'period']
