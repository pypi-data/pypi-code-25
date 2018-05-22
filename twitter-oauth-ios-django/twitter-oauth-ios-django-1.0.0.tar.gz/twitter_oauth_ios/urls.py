from django.urls import path
from .views import AuthView


app_name = 'twitter_oauth_ios'


urlpatterns = [
    path('', AuthView.as_view(), name='auth_view'),
]
