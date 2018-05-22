from django.urls import include, path

urlpatterns = [
    path('', include('twitter_oauth_ios.urls', namespace='twitter_oauth_ios')),
]
