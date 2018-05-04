from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse

@api_view(['GET'])
def get_apps(request):
    '''
    List the installed apps for the UI.
    :return: A list of the installed apps on the system (excluding django
    apps).
    '''
    apps = [setting for setting in settings.INSTALLED_APPS \
            if 'django.' not in setting]
    return Response(apps)

