"""
bomojo test views

This module defines a dummy login view for the tests, since some of the views
in the API require authentication.
"""

from django.http import HttpResponse


def login(request):
    return HttpResponse('oh hai there')
