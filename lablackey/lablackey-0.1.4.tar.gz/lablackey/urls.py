from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from django.contrib.staticfiles.views import serve
from django.db.utils import ProgrammingError

admin.autodiscover()

import views

urlpatterns = [
  #url(r'^api/schema/([\w\d]+).([\w\d]+)/$',views.get_schema),
  url(r'^set_email/$',views.set_email ,name='set_email'),
  url(r'^user.json$',views.user_json),
  url(r'^accounts/logout/$',views.logout),
  url(r'favicon.ico$', views.redirect,
      {'url': getattr(settings,'FAVICON','/static/favicon.png')}),
  url(r'^admin/', include(admin.site.urls)),
  url(r'^$',views.render_template,kwargs={'template': "base.html"}),
  url(r'^auth/', include(auth_urls)),
  url(r'^auth/login_ajax/$',views.login_ajax,name='login_ajax'),
  url(r'^auth/login/$',views.single_page_app,name="login"),
]

if 'lablackey.registration' in settings.INSTALLED_APPS:
  from lablackey.registration import urls as registration_urls
  urlpatterns += [
    url(r'^auth/',include(registration_urls)),
    url(r'^accounts/', include(registration_urls,namespace="depracated")),#! Depracated in favor of auth
  ]

if 'lablackey.api' in settings.INSTALLED_APPS:
  from lablackey.api import views as api_views
  from lablackey.api.urls import build_urls
  urlpatterns += [
    url(r'^durf/([\w\d]+)/([\w\d]+)/$',api_views.get_many),
    url(r'^durf/([\w\d]+)/([\w\d]+)/(\d+)/$',api_views.get_one),
    url(r'^api/schema/([\w\d\.]+)\.([\w\d]+Form)/$',views.get_form_schema,name="ur_form_add"),
    url(r'^api/schema/([\w\d\.]+)\.([\w\d]+Form)/(\d+)/$',views.get_form_schema,name="ur_form_schema"),
    url(r'^api/schema/([\w\d]+)\.([\w\d]+)/$',views.get_schema),
    url(r'^form/([\w\d\.]+)([\w\d]+Form)/$',views.render_template,name="ur-form"),
  ]
  urlpatterns += build_urls()

if "social.apps.django_app.default" in settings.INSTALLED_APPS:
  import social.apps.django_app.urls
  urlpatterns.append(url('', include(social.apps.django_app.urls, namespace='social')))

if 'social_django' in settings.INSTALLED_APPS:
  import social_django.urls
  urlpatterns.append(url('', include(social_django.urls, namespace='social')))

if 'lablackey.blog' in settings.INSTALLED_APPS:
  import lablackey.blog.urls
  urlpatterns.append(url(r'^blog/',include(lablackey.blog.urls)))

if 'airbrake' in settings.INSTALLED_APPS:
  import airbrake.urls
  urlpatterns.append(url(r'',include(airbrake.urls)))

if 'django.contrib.flatpages' in settings.INSTALLED_APPS:
  from django.contrib.flatpages.models import FlatPage
  import django.contrib.flatpages.views
  # this breaks on initial migration before flatpages are migrated
  try:
    fps = '|'.join([page.url[1:] for page in FlatPage.objects.all()])
    urlpatterns.append(url(r'^(%s)$'%fps,django.contrib.flatpages.views.flatpage,name='map'))
  except ProgrammingError:
    pass

if settings.DEBUG:
  from django.views.static import serve
  urlpatterns += [
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
  ]
