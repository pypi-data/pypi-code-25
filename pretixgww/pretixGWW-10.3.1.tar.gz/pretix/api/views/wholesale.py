from rest_framework import viewsets
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.template.loader import render_to_string
from pretix.api.serializers.event import WholesaleAccountsSerializer
from pretix.base.models.wholesale import WholesaleAccounts
from pretix.base.models import Event
from django.conf import settings
from pretix.api.serializers.pos import Opening_closing_balanceSerializer
from pretix.base.models.pos import  Opening_closing_balance


from rest_framework.response import Response


@api_view(['GET'])
def wholesale_list(request,*args,**kwargs):
    model_obj = WholesaleAccounts.objects.filter(event_id=Event.objects.get(slug=kwargs['event']).id)
    model_data = WholesaleAccountsSerializer(model_obj, many=True).data
    return Response({"data": model_data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def wholesale_view(request,*args,**kwargs):
    model_obj = WholesaleAccounts.objects.get(id=kwargs['id'])
    model_data = WholesaleAccountsSerializer(model_obj).data
    return Response({"data": model_data}, status=status.HTTP_200_OK)


@api_view(['Delete'])
def wholesale_delete(request,*args,**kwargs):
    try:
        instance = WholesaleAccounts.objects.get(id=kwargs['id'])
        instance.delete()
        return Response({"data": "Deleted Successfully"}, status=status.HTTP_200_OK)
    except:
        error_message = "This object can't be deleted!!"
        return Response({"data": error_message}, status=status.HTTP_400_BAD_REQUEST)
        # return Response(error_message)


@api_view(['PUT'])
def wholesale_update(request,*args,**kwargs ):
    instance = WholesaleAccounts.objects.get(id=kwargs['id'])
    serializer = WholesaleAccountsSerializer(instance, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    else:
        error_details = []
        for key in serializer.errors.keys():
            error_details.append({"field": key, "message": serializer.errors[key][0]})
        data = {
            "Error": {
                "status": 400,
                "message": "Your  data was not valid - please correct the below errors",
                "error_details": error_details
            }
        }
        return Response({"data": data}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def wholesale_account_type(request,*args,**kwargs):
    ACCOUNT_TYPE = settings.ACCOUNT_TYPE
    return Response({"data": ACCOUNT_TYPE}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def wholesale_create(request,*args,**kwargs):
    event_id=Event.objects.get(slug=kwargs['event']).id
    request.data['event'] = event_id
    serializer = WholesaleAccountsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(event=Event.objects.get(pk=event_id))
        if request.accepted_renderer.format == 'html':
            # here you will provide the template name to render ui page
            return Response(data=[])
        return Response({"data": "Data added successfully"}, status=status.HTTP_201_CREATED)
    else:
        error_details = []
        for key in serializer.errors.keys():
            error_details.append({"field": key, "message": serializer.errors[key][0]})
        data = {
            "Error": {
                "status": 400,
                "message": "Your  data was not valid - please correct the below errors",
                "error_details": error_details
            }
        }
        if request.accepted_renderer.format == 'html':
            pass
        return Response(data, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
def opening_balance(request,*args,**kwargs):
    custom_filter = {}
    #custom_filter['deleted'] = 0
    try:
        if request.data['cashier_name']:
            custom_filter['cashier_name'] = request.data['cashier_name']

        if request.data['date']:
            custom_filter['date'] = request.data['date']

        if kwargs['event']:
            event = Event.objects.get(slug=kwargs['event'])
            custom_filter['event'] = event.id

    except:
        pass
    model_obj = Opening_closing_balance.objects.filter(**custom_filter).order_by("-id")[:1]
    model_data = Opening_closing_balanceSerializer(model_obj, many=True).data
    return Response({"data":{"opening_data":model_data,"credit":100,"cash":1000}}, status=status.HTTP_200_OK)