from django.conf.urls import patterns, url
from molo.globalsite import views


urlpatterns = patterns(
    '',
    url(r'^countries/$', views.CountryView.as_view(),
        name='country_selection'),

    url(r'^setcountry/(?P<country_code>[\w-]+)/$',
        views.set_country, name='set_country'),

    url(r'^changecountry/$', views.change_country, name='change_country'),
)
