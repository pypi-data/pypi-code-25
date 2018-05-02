from django.urls import path

from . import views

urlpatterns = [
    path(r'<slug:shortname>', views.index, name='index'),
]

