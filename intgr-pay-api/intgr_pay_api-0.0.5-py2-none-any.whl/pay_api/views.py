# -*- coding: utf-8 -*-
from django.http.response import HttpResponse
from django.views.generic.base import View
from pay_api.backends.payu import post as payu_post_handler
from pay_api.backends.paypal import post as paypal_post_handler
from pay_api.backends.dotpay import post as dotpay_post_handler

class NotifyView(View):
    def post(self, request, *args, **kwargs):
        
        if 'application/json' in request.META['CONTENT_TYPE']:
            
            if 'HTTP_PAYPAL_TRANSMISSION_SIG' in request.META.keys():
                return paypal_post_handler(request, *args, **kwargs)
            
            if 'HTTP_OPENPAYU_SIGNATURE' in request.META.keys():
                return payu_post_handler(request, *args, **kwargs)
            
        return dotpay_post_handler(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        return HttpResponse("Forbidden", status = 403)
