from django.urls import path

from packrat import views

urlpatterns = [
    path('md5/<hsh>', views.md5, name='md5'),
]
