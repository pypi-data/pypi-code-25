from django.shortcuts import get_object_or_404
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from pretix.base.models.pos import  Opening_closing_balance
from pretix.base.models import  Item,Order,Event,User
from rest_framework import status
from pretix.api.serializers.pos import Opening_closing_balanceSerializer
from rest_framework.response import Response
from rest_framework import viewsets, generics, serializers
from rest_framework.decorators import api_view, permission_classes

class OpeenclosebalanceViewSet(viewsets.ModelViewSet):
    #renderer_classes = [TemplateHTMLRenderer]
    #template_name = 'profile_detail.html'

    serializer_class = Opening_closing_balanceSerializer
    queryset = Opening_closing_balance.objects.none()
    ordering_fields = ('date', 'user','event')
    ordering = ('id',)



    def get_queryset(self):
        return Opening_closing_balance.objects.all()

    def create(self, request, *args,**kwargs):
        event = Event.objects.get(slug=kwargs['event'])
        request.data['event']=event.id
        serializer = Opening_closing_balanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args,**kwarg):
        pk=kwarg['pk']
        instance=Opening_closing_balance.objects.get(pk=pk)
        serializer = Opening_closing_balanceSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        #return Response({"return": "post"})

    def retrieve(self, request, *args,**kwarg):
        model_obj = Opening_closing_balance.objects.get(pk=kwarg['pk'])
        model_data = Opening_closing_balanceSerializer(model_obj).data
        return Response({"data": model_data}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args,**kwarg):
        pk = kwarg['pk']
        instance = Opening_closing_balance.objects.get(pk=pk)
        serializer = Opening_closing_balanceSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args,**kwarg):
        return Response({"return": "post"})

