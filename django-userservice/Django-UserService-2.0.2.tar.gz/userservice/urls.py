from django.conf.urls import include, url
from userservice.views import support

urlpatterns = [
    url(r'', support, name="userservice_override"),
]
