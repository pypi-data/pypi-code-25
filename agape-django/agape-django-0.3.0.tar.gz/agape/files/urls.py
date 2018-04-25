from django.conf.urls import url, include
from .views import FileViewSet

# build router
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'files', FileViewSet, base_name='files')

urlpatterns = [
    url(r'^',include(router.urls)),
]