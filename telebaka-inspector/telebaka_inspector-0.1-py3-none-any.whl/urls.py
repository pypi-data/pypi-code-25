from django.urls import path

from telebaka_inspector.views import InspectorView


app_name = 'telebaka_inspector'

urlpatterns = [
    path('<pk>/', InspectorView.as_view(), name='inspector')
]
