from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^u/?$', views.userList, name='userlist'),
    url(r'^u/(?P<userId>\d+)/?$', views.userProfile, name='profile'),
    url(
        r'^u/(?P<userId>\d+)/(?P<nick>[^/]+)/?$',
        views.userProfile, name='profile'),
    url(r'^g/?$', views.gameList, name='gamelist'),
    url(r'^g/(?P<gameId>\d+)/?$', views.viewGame, name='viewgame'),
    url(r'^a/(?P<arenaId>\d+)/?$', views.arena, name='arena'),
    url(r'^ajax/pausearena$', views.pauseArena, name='pausearena'),
    url(r'^ajax/resumearena$', views.resumeArena, name='resumearena'),
    url(r'^ajax/restartarena$', views.restartArena, name='restartarena'),
    url(r'^ajax/resetarena', views.resetArena, name='resetarena'),
    url(r'^ajax/disablearena$', views.disableArena, name='disablearena'),
    url(r'^ajax/enablearena$', views.enableArena, name='enablearena'),
    url(r'^ajax/disableshots$', views.disableShots, name='disableshots'),
    url(r'^ajax/enableshots', views.enableShots, name='enableshots'),
    url(r'^ajax/disablecaps$', views.disableCaps, name='disablecaps'),
    url(r'^ajax/enablecaps$', views.enableCaps, name='enablecaps'),
]

