from rest_framework import viewsets
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.template.loader import render_to_string
from pretix.api.serializers.order import OrderSerializer
from pretix.api.serializers.voucher import  VoucherSerializer
from pretix.base.models import Event,Order,Item,Voucher
from django.conf import settings
from rest_framework.response import Response
import  json
from django.core import serializers
from django.db.models import Q
from datetime import datetime

@api_view(['GET','POST'])
def order_print_status_update(request,*args,**kwargs):
    order_code=kwargs['pk']
    model_obj = Order.objects.get(code=order_code)
    model_obj.printed_status=True
    model_obj.save()
    return Response({"data": "Changed successfully"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def couponcodes(request,*args,**kwargs):
    items=request.data['items']
    today = datetime.today()
    event_id = Event.objects.get(slug=kwargs['event']).id
    model_obj=Voucher.objects.filter(item_id__in=items,event=event_id).filter(Q(valid_until__gte=today))
    voucher_list=[]
    for voucher in model_obj:
        item_name= Item.objects.get(pk=voucher.item_id)
        item_name_val=item_name.name;
        #   item_name_val=json.loads(item_name_val)
        voucher_dict={
            "id":voucher.id,
            "code":voucher.code,
            "item": voucher.item_id,    

            "valid_until": voucher.valid_until,
            "redeemed": voucher.redeemed,
            "block_quota": voucher.block_quota,
            "value": voucher.value,
            "comment": voucher.comment,
            "max_usages": voucher.max_usages,
            "subevent": voucher.subevent,
            "price_mode": voucher.price_mode,
            "tag": voucher.tag,
            "quota":voucher.quota
        }
        voucher_list.append(voucher_dict)
    return Response({"data": voucher_list}, status=status.HTTP_200_OK)


@api_view(['POST'])
def userwise_order_list(request,*args,**kwargs):
    user_id=request.data['user_id']
    event_id = Event.objects.get(slug=kwargs['event']).id
    pending = Order.objects.filter(status='n',created_by=user_id,event_id=event_id)
    paid = Order.objects.filter(status='p',created_by=user_id,event_id=event_id)
    cancel = Order.objects.filter(status='c',created_by=user_id,event_id=event_id)
    expried = Order.objects.filter(status='e',created_by=user_id,event_id=event_id)
    refund = Order.objects.filter(status='r',created_by=user_id,event_id=event_id)
    pending_data = OrderSerializer(pending, many=True).data
    paid_data = OrderSerializer(paid, many=True).data
    cancel_data = OrderSerializer(cancel, many=True).data
    expried_data = OrderSerializer(expried, many=True).data
    refund_data = OrderSerializer(refund, many=True).data
    sending_data={
        "pending_data":pending_data,
        "pending_data_count":len(pending_data),
        "paid_data":paid_data,
        "paid_data_count":len(paid_data),
        "cancel_data":cancel_data,
        "cancel_data_count":len(cancel_data),
        "expried_data":expried_data,
        "expried_data_count":len(expried_data),
        "refund_data":refund_data,
        "refund_data_count":len(refund_data),
    }
    return Response({"data": sending_data}, status=status.HTTP_200_OK)