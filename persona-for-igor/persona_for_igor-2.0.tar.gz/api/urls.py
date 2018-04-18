from api import views

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet)
router.register(r'hubs', views.HubViewSet)
router.register(r'personas_to_hubs', views.PersonasToHubsViewSet)
router.register(r'feeder_processed_articles_urls', views.FeederProcessedArticlesUrlsViewSet)



# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r'^', include(router.urls)),

]
