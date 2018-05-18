from django.conf.urls import url

from .views import MySettingsView
from .views import MyTicketsView

settingsView = MySettingsView.as_view()
ticketsView = MyTicketsView.as_view()

urlpatterns = [
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/pretix_mabel/settings',
        settingsView, name='settings'),
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/pretix_mabel/tickets',
        ticketsView, name='tickets'),
]
