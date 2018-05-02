from . import views
from django.urls import path

app_name = 'unicampauth'

urlpatterns = [
    path('authorize/', views.Authorize.as_view(), name='authorize'),
    path('callback/', views.ExchangeCode.as_view(), name='callback')
]
