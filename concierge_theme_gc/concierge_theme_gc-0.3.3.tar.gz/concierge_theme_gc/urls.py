from django.conf.urls import url

import views

urls = [
    url(r'^termsofuse/$', views.terms_of_use, name='terms_of_use'),
    url(
        r'^accept_previous_logins/(?P<acceptation_token>[-:\w]+)/$',
        views.accept_previous_login,
        name='accept_previous_login'
    ),
]
