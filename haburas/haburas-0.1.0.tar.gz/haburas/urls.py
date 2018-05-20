
from django.urls import path

from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.Index.as_view()), name='index'),
    path('create/', login_required(views.Create.as_view()), name='create'),
]
