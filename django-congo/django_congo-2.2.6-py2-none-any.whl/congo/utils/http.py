# -*- coding: utf-8 -*-
from django.http.response import HttpResponse

class HttpResponseServiceUnavailable(HttpResponse):
    status_code = 503
