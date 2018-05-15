# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from bigtree_sso.views import SessionSSOView, CodeSSOView, DebugCodeSSOView

urlpatterns = patterns(
    'bigtree_sso.views',
    url(r'^code/$', CodeSSOView.as_view(), name='code_sso'),
    url(r'^debug_code/$', DebugCodeSSOView.as_view(), name='debug_code_sso'),
    url(r'^session/$', SessionSSOView.as_view(), name='session_sso'),
)
