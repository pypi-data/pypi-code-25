from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.authtoken.models import Token
from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate
from rest_framework import authtoken
from pretix.base.models import Team,TeamAPIToken
from django.core import serializers
from pretix.api.serializers.event import WholesaleAccountsSerializer
from pretix.base.models.wholesale import WholesaleAccounts
from pretix.base.models import Event
from rest_framework.decorators import api_view, permission_classes
import json

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Login failed"}, status=HTTP_401_UNAUTHORIZED)
        #member=Team.members.all()
        teams=Team.members.through.objects.filter(user=user)
        if len(teams)>0:
            team = teams[0].team_id;
            tokens=TeamAPIToken.objects.filter(team_id=team,active=1)
            user_details={"full_name":user.fullname,"email":user.email,"id":user.id}
            if len(tokens)>0:
                tokens_list=[]
                for field in tokens:
                    tokens_list.append({"token":field.token,"team_id":field.team_id,"team_name":Team.objects.get(pk=field.team_id).name})
                return Response({"tokens":tokens_list,"user_datails":user_details})
            else:
                return Response({"error": "Token Id Not Generated"}, status=HTTP_401_UNAUTHORIZED)

        else:
            return Response({"error": "Login failed"}, status=HTTP_401_UNAUTHORIZED)

