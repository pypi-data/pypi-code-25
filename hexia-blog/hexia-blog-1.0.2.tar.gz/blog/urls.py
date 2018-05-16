from django.conf.urls import url

from blog.views import *


app_name = 'blog'
urlpatterns = [
    url(r'^list/$', BlogListView.as_view(), name="blog-list"),
    url(r'^write/$', BlogCreateView.as_view(), name='blog-create'),
    url(r'^(?P<slug>[\w\\-]+)/$', BlogDetailView.as_view(), name="blog-detail"),
    
]