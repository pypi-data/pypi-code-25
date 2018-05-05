from django.conf.urls import url
from . import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'win.views.home', name='home'),
    url(r'^$', views.poll_index, name='poll'),
    url(r'^statistics/$', views.statistics, name='statistics'),
    url(r'^statistics/get_data/$', views.get_data, name='get_data'),
]
