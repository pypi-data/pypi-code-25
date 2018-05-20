from django.conf.urls import (
    include,
    url,
)

from .views import (
    calls,
    notifications,
    reviews,
    submissions,
)


app_name = 'submitify'
notification_urls = [
    url(r'^(?P<notification_id>\d+)/$', notifications.view_notification,
        name='view_notification'),
    url(r'^(?P<notification_type>(basic|accept|reject))/$',
        notifications.send_notification,
        name='send_notification'),
]

review_urls = [
    url(r'^create/$', reviews.create_review,
        name='create_review'),
    url(r'(?P<review_id>\d+)/$', reviews.view_review,
        name='view_review'),
    url(r'(?P<review_id>\d+)/edit/$', reviews.edit_review,
        name='edit_review'),
]

submission_urls = [
    url(r'^$', submissions.view_submission,
        name='view_submission'),
    url(r'^text/$', submissions.view_submission_text,
        name='view_submission_text'),
    url(r'^pdf/$', submissions.view_submission_file,
        name='view_submission_file'),
    url(r'^original/$', submissions.view_original_file,
        name='view_original_file'),
    url(r'^reviews/', include(review_urls)),
    url(r'^resolve/(?P<resolution_type>(accept|reject))/$',
        submissions.resolve_submission,
        name='resolve_submission'),
]

call_urls = [
    url(r'^$', calls.view_call,
        name='view_call'),
    url(r'^submit/$', submissions.create_submission,
        name='create_submission'),
    url(r'^edit/$', calls.edit_call,
        name='edit_call'),
    url(r'^next/$', calls.next_step,
        name='next_step'),
    url(r'^notifications/', include(notification_urls)),
    url(r'^(?P<submission_id>\d+)/', include(submission_urls))
]

urlpatterns = [
    url(r'^$', calls.list_calls,
        name='list_calls'),
    url(r'^create/$', calls.create_call,
        name='create_call'),
    url(r'^invite/reader/$', calls.invite_reader,
        name='invite_reader'),
    url(r'^invite/writer/$', calls.invite_writer,
        name='invite_writer'),
    url(r'^(?P<call_id>\d+)/', include(call_urls)),
    url(r'^(?P<call_id>\d+)-(?P<call_slug>[-\w]+)/', include(call_urls)),
]
