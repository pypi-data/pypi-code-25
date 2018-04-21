from django.conf.urls import *

import lablackey.views
import views

urlpatterns = [
  url(r'^$', views.index, name="event_index"),
  url(r'^(\d+\-\d+\-\d+)/$', views.index, name="event_index"),
  url(r'^occurrence/(\d+)/$', views.occurrence_detail,name='occurrence_detail'),
  url(r'^(\d+)/(.+)/$', views.occurrence_detail,name='occurrence_detail'),
  url(r'ics/([^/]+)/([^/]+)/(\d+)/(.+).ics', views.ics,name="event_ics"),
  url(r'ics/(all_events).ics', views.all_ics,name="event_all_ics"),
  url(r'eventdetail_(\d+).json', views.detail_json),
  #url(r'weekly/(\d+\-\d+\-\d+)/', views.weekly,name="weekly"),
  #url(r'weekly/(\d+\-\d+\-\d+)/(?P<page_number>\d+)/',views.weekly,name="weekly"),
  #url(r'^(?P<page_number>\d+)/$', views.index, name="event_list"),
  #url(r'^tagged/(?P<slug>[^/]+)/(?P<page_number>\d+)/$', views.index, name="tagged"),
  url(r'^detail/(\d+)/(.+)/$', views.detail, name="event_detail"),
  url(r'^rsvp/$', views.rsvp, name='event_rsvp'),
  url(r'^checkin/$', views.checkin, name='event_rsvp'),
  url(r'^(own|disown)/(\d+)/',views.owner_ajax),
  url(r'^bulk.json$',views.bulk_ajax),

  url(r'^schedule/$',lablackey.views.single_page_app,name="conference"),
  url(r'^conference.json$',views.conference_json,name="conference.json"),
]
