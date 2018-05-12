from rest_framework import viewsets
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.template.loader import render_to_string
from pretix.api.serializers.order import OrderSerializer
from pretix.base.models import Event,Order
from django.conf import settings
from rest_framework.response import Response


@api_view(['GET','POST'])
def order_print_status_update(request,*args,**kwargs):
    order_code=kwargs['pk']
    model_obj = Order.objects.get(code=order_code)
    model_obj.printed_status=True
    model_obj.save()

    return Response({"data": "Changed successfully"}, status=status.HTTP_200_OK)