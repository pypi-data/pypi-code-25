import importlib

from django.apps import apps
from django.conf.urls import include, url
from rest_framework import routers

from .views import checkin, event, item, order, organizer, voucher, waitinglist, sms, team,wholesale,pos

router = routers.DefaultRouter()
router.register(r'organizers', organizer.OrganizerViewSet)

orga_router = routers.DefaultRouter()
orga_router.register(r'events', event.EventViewSet)

event_router = routers.DefaultRouter()
event_router.register(r'subevents', event.SubEventViewSet)
event_router.register(r'items', item.ItemViewSet)
event_router.register(r'categories', item.ItemCategoryViewSet)
event_router.register(r'questions', item.QuestionViewSet)
event_router.register(r'quotas', item.QuotaViewSet)
event_router.register(r'vouchers', voucher.VoucherViewSet)
event_router.register(r'orders', order.OrderViewSet)
event_router.register(r'orderpositions', order.OrderPositionViewSet)
event_router.register(r'invoices', order.InvoiceViewSet)
event_router.register(r'taxrules', event.TaxRuleViewSet)
event_router.register(r'waitinglistentries', waitinglist.WaitingListViewSet)
event_router.register(r'checkinlists', checkin.CheckinListViewSet)

checkinlist_router = routers.DefaultRouter()
checkinlist_router.register(r'positions', checkin.CheckinListPositionViewSet)

question_router = routers.DefaultRouter()
question_router.register(r'options', item.QuestionOptionViewSet)

item_router = routers.DefaultRouter()
item_router.register(r'variations', item.ItemVariationViewSet)
item_router.register(r'addons', item.ItemAddOnViewSet)

# Force import of all plugins to give them a chance to register URLs with the router
for app in apps.get_app_configs():
    if hasattr(app, 'PretixPluginMeta'):
        if importlib.util.find_spec(app.name + '.urls'):
            importlib.import_module(app.name + '.urls')
from .views import  wholesale
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^organizers/(?P<organizer>[^/]+)/', include(orga_router.urls)),
    url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/', include(event_router.urls)),
    url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/items/(?P<item>[^/]+)/', include(item_router.urls)),
    url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/vouchers/(?P<voucher>[^/]+)/redeem/',
        voucher.RedeemViewSet.as_view(), name='redeem'),
    url(r'^teams/teamapitoken/(?P<token>[^/]+)/', team.TeamTokenAPIView.as_view(), name='teamapitoken'),
    url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/sms/', sms.OrderDetailSmsView.as_view(), name='sms'),
    url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/questions/(?P<question>[^/]+)/',
        include(question_router.urls)),
    url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/checkinlists/(?P<list>[^/]+)/',
        include(checkinlist_router.urls)),  url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/wholesale/list',  wholesale.wholesale_list, name='wholesale_list'),
    url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/wholesale/update/(?P<id>[^/]*)/$',  wholesale.wholesale_update, name='wholesale_update'),
    url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/wholesale/delete/(?P<id>[^/]*)/$',  wholesale.wholesale_delete, name='wholesale_delete'),
    url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/wholesale/create/',wholesale.wholesale_create, name='wholesale_create'),
    url(r'^organizers/(?P<organizer>[^/]+)/events/(?P<event>[^/]+)/wholesale/view/(?P<id>[^/]*)/$',wholesale.wholesale_view, name='wholesale_view'),
    url(r'^wholesale/wholesale_account_type/', wholesale.wholesale_account_type, name='wholesale_account_type'),
    #url(r'^login/', pos.login, name='login'),
    url(r'^login/', pos.CustomAuthToken.as_view())

]