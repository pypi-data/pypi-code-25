# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from bomojo.matchups.models import Matchup


class MatchupAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'description', 'featured', 'created_on')


admin.site.register(Matchup, MatchupAdmin)
