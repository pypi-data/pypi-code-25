from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from rest_framework import serializers, generics, status
from rest_framework.response import Response
from twilio.rest import Client

from pretix.api.serializers.sms import OrderDetailSmsSerializer
from pretix.base.models import Order


class OrderDetailSmsView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderDetailSmsSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['region'] == 'IN':
                to = '+91%s' % serializer.validated_data['phone']
            else:
                to = '+1%s' % serializer.validated_data['phone']
            try:
                order = Order.objects.get(pk=serializer.validated_data['order'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError(_("Order doesn't exist."))
            url = '%(base_url)s/%(organizer)s/%(event)s/order/%(code)s/%(secret)s' % \
                  {
                      "base_url": settings.SITE_URL,
                      "organizer": kwargs['organizer'],
                      "event": kwargs['event'],
                      "code": order.code,
                      "secret": order.secret
                  }
            message = 'Your Order is successfully placed with order id BE8MOLGS. Please follow below link to check ' \
                      'details  of your order %s' % url
            try:
                client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                sms = client.messages.create(
                    to=to,
                    from_='+15103190303',
                    body=message
                )
                return Response({'sms_sid': sms.sid}, status=status.HTTP_201_CREATED)
            except:
                return Response({'error': 'Invalid phone number.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid params'}, status=status.HTTP_400_BAD_REQUEST)