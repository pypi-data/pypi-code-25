from urllib.parse import urljoin
from base64 import b32encode
from binascii import unhexlify

from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, update_session_auth_hash
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import messages
from django.template.response import TemplateResponse
from django.contrib.auth import password_validation


from django_otp.util import random_hex
import django_otp

from core.models import User, ResizedAvatars, PreviousLogins, PleioLegalText

from saml.models import IdentityProvider, IdpEmailDomain
from two_factor.views import ProfileView
from user_sessions.views import SessionListView
from two_factor.views.profile import DisableView


def avatar(request):
    avatar_size = request.GET.get('size')
    DEFAULT_AVATAR = '/static/images/user.svg'

    user = User.objects.get(id=request.GET.get('guid'))

    try:
        user = User.objects.get(id=int(request.GET['guid']))
        if user.avatar:
            try:
                resized_avatars = ResizedAvatars.objects.get(user=user)
                if avatar_size == 'large':
                    avatar = resized_avatars.large
                elif avatar_size == 'small':
                    avatar = resized_avatars.small
                elif avatar_size == 'tiny':
                    avatar = resized_avatars.tiny
                elif avatar_size == 'topbar':
                    avatar = resized_avatars.topbar
                else: #when no size is requested, medium will be served
                    avatar = resized_avatars.medium

                return redirect('/media/' + str(avatar))
            except ResizedAvatars.DoesNotExist:
                pass
    except User.DoesNotExist:
        pass

    return redirect(DEFAULT_AVATAR)

def accept_previous_login(request, acceptation_token=None):
    try:
        PreviousLogins.accept_previous_logins(request, acceptation_token)
    except:
        pass

    return redirect('profile')


def terms_of_use(request):

    return render(request, 'terms_of_use.html')
