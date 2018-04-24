from django.conf.urls import url

from .views import get_swagger_view

urlpatterns = [
    url(r'^$', get_swagger_view()),
]
