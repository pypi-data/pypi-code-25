# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import AuthenticationForm

from rest_framework import decorators

from .helpers import kong_login, get_auth_data

import requests, json

def index(request):
    data = {}
    for key, value in request.META.items():
        if key.startswith('HTTP_X_'):
            data[key] = value
    data['user_id'] = request.user.id
    data['is_authenticated'] = request.user.is_authenticated()
    return JsonResponse(data)

@decorators.api_view(['GET', 'POST'])
@csrf_exempt
def token(request):

    next = request.GET.get('next')

    if request.method == 'GET':
        form = AuthenticationForm()
        context = {"form": form}
        return render(request, 'kong_oauth/login.html', context = context)

    data = get_auth_data(request.data)
    user = authenticate(request, **data)
    if user is not None:
        client_id = request.data.get('client_id')
        client_secret = request.data.get('client_secret')
        result, status = kong_login(user, client_id, client_secret)
        result.update({
            "data": user.data
        })
    else:
        result = { 'message': 'Authentication failed. Invalid username or password' }
        status = 401

    return JsonResponse(result, status=status)

