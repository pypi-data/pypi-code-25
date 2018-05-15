from django.urls import path
from .views import index, article


app_name = 'pyninjas_blog'


urlpatterns = [
    path('tags/<tag>/', index, name='tag'),
    path('<slug>/', article, name='article'),
    path('', index, name='index'),
]
