from django.conf.urls import url, include
from .views import handle_uploaded_file, upload_file, upload_img

urlpatterns = [
    url(r'^__upload_img/$', upload_img),
    url(r'^__upload_file/$', upload_file),
]