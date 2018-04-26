# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page

from matchups.forms import MatchupForm
from matchups.models import Matchup
from matchups.utils import get_avatar_url


class MatchupsView(View):
    def get(self, request):
        featured_matchups = Matchup.objects.filter(featured=True)
        recent_matchups = featured_matchups.order_by('-created_on')[:20]
        return JsonResponse([_render_matchup(matchup)
                             for matchup in recent_matchups], safe=False)

    def post(self, request):
        form = MatchupForm(request.JSON)
        if form.is_valid():
            matchup = form.save()
            return JsonResponse(_render_matchup(matchup), status=201)
        else:
            return JsonResponse({'errors': form.errors}, status=400)


class MatchupView(View):
    @method_decorator(cache_page(60 * 60))
    def get(self, request, slug):
        try:
            matchup = Matchup.objects.get(slug=slug)
            return JsonResponse(_render_matchup(matchup))
        except Matchup.DoesNotExist:
            return JsonResponse({
                'errors': {
                    'slug': ['That matchup does not exist.']
                }
            }, status=404)


def _render_matchup(matchup):
    result = {
        'slug': matchup.slug,
        'title': matchup.title,
        'description': matchup.description,
        'avatar': '',
        'movies': matchup.movies,
        'period': matchup.period,
        'created': matchup.created_on.isoformat()
    }

    if matchup.email:
        result['avatar'] = get_avatar_url(matchup.email)

    return result
