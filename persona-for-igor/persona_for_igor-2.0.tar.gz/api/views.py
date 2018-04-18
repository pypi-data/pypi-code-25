from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import renderers, viewsets, filters
from rest_framework.response import Response
from rest_framework import permissions
from api.permissions import IsOwnerOrReadOnly
from newtable.models import Account, PersonasToHubs, Hub
from personas.models import FeederProcessedArticlesUrls
from api.serializers import AccountSerializer, HubSerializer, PersonasToHubsSerializer, \
    FeederProcessedArticlesUrlsSerializer
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import mixins


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('email',)


class HubViewSet(viewsets.ModelViewSet):
    queryset = Hub.objects.all()
    serializer_class = HubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('account',)


class PersonasToHubsViewSet(viewsets.ModelViewSet):
    queryset = PersonasToHubs.objects.all()
    serializer_class = PersonasToHubsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('personas',)


class FeederProcessedArticlesUrlsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FeederProcessedArticlesUrls.objects.all()
    serializer_class = FeederProcessedArticlesUrlsSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['url',]

