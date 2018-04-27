# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.cache import cache_page

import pybomojo


@cache_page(60 * 60 * 24)
def search(request):
    if 'title' not in request.GET:
        return HttpResponseBadRequest('"title" is required')

    search_term = request.GET['title']
    results = pybomojo.search_movies(search_term)

    # Move exact result to the top. This is very inefficient, but it'll get the
    # job done for now. (The more efficient code would be slightly uglier.)
    results = ([result for result in results if result['exact']] +
               [result for result in results if not result['exact']])

    return JsonResponse({'results': results})


@cache_page(60 * 15)
def box_office(request, movie_id):
    try:
        return JsonResponse(pybomojo.get_box_office(movie_id))
    except pybomojo.MovieNotFound as e:
        return JsonResponse({'errors': [str(e)]}, status=404)
