from django.conf.urls import url
from . import views

app_name = 'telegram_bots'
urlpatterns = [
    url(
        regex=r'^$',
        view=views.BotListView.as_view(),
        name='telegram_bots_list',
    ),
    url(
        regex=r'^(?P<pk>\d+)/$',
        view=views.BotDetailView.as_view(),
        name='telegram_bots_detail',
    ),
    url(
        regex=r'^create/$',
        view=views.BotCreateView.as_view(),
        name='telegram_bots_create',
    ),
    url(
        regex=r'^(?P<pk>\d+)/delete/$',
        view=views.BotDeleteView.as_view(),
        name='telegram_bots_delete',
    ),
    url(
        regex=r'^subscribe/(?P<signature>.+)/$',
        view=views.BotSubscribeView.as_view(),
        name='telegram_bots_subscribe'
    ),
    url(
        regex=r'^unsubscribe/(?P<signature>.+)/$',
        view=views.BotUnsubscribeView.as_view(),
        name='telegram_bots_unsubscribe'
    ),
    url(
        regex=r'^(?P<bot_token>.+)/$',
        view=views.ReceiveView.as_view(),
        name='telegram_bots_receiver'
    ),
]
