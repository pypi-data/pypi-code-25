from django.conf.urls import url
from django.urls import include, path
from . import views

app_name = "feedback"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
]
