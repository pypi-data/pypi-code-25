from django.conf.urls import url, patterns

urlpatterns = patterns(
  'lablackey.db.views',
  url('^admin/merge_model/(.*)/(.*)/$','merge_model')
)
