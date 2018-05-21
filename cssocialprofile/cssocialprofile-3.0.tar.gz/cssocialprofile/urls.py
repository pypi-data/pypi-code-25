from django.conf.urls import include, url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from cssocialprofile import views


#default view for our index
urlpatterns = [
    url(r'^$', views.index, name="cssocialprofile_index"),
]

#register and social urls
urlpatterns += [
    url(r'^logout$', auth_views.logout, name='cssocialprofile_logout'),
    url(r'^login$', auth_views.login, name='cssocialprofile_user_login'),

    url(r'^accounts/', include('registration.backends.default.urls')),
    url('', include('social_django.urls', namespace='social'))
]

#default profile edit urls
urlpatterns += [
    url(r'^edit-profile$', views.edit_profile, name='cssocialprofile_edit_profile'),
    url(r'^edit-profile-photo$', views.edit_profile_photo, name='cssocialprofile_edit_profile_photo'),
    url(r'^edit-profile-social$', views.edit_profile_social, name='cssocialprofile_edit_profile_social'),
]


