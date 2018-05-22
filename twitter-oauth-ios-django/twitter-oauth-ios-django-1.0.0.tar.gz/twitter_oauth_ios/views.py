from datetime import datetime
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from social_django.models import UserSocialAuth
from .forms import TwitterAuthForm

import json


class AuthView(View):
    form_class = TwitterAuthForm
    user_model = get_user_model()

    def put(self, request, *args, **kwargs):
        body = json.loads(request.body.decode('utf-8'))
        body['auth_time'] = int(datetime.now().strftime('%s'))
        form = self.form_class(body)

        if not form.is_valid():
            return JsonResponse({'result': 'error'}, status=400)

        social_auth = UserSocialAuth.get_social_auth(provider='twitter', uid=form.data['user_id'])

        if social_auth:
            user = social_auth.user
            user.username = form.data['screen_name']
            user.first_name = form.data['display_name']
            user.save()
            social_auth.user = user

            extra_data = social_auth.extra_data
            extra_data['auth_time'] = form.data['auth_time']
            extra_data['access_token']['screen_name'] = form.data['screen_name']

            social_auth.extra_data = extra_data
            social_auth.save()

            return JsonResponse({'result': 'success'})

        user = self.user_model.objects.create_user(
            username=form.data['screen_name'],
            first_name=form.data['display_name'],
            is_active=True)
        user.save()

        extra_data = {
            'auth_time': form.data['auth_time'], 'id': form.data['user_id'],
            'access_token': {
                'oauth_token': form.data['oauth_token'],
                'oauth_token_secret': form.data['oauth_token_secret'],
                'user_id': form.data['user_id'],
                'screen_name': form.data['screen_name']
            }
        }
        social_auth = UserSocialAuth(user=user, provider='twitter', uid=form.data['user_id'], extra_data=extra_data)
        social_auth.save()

        return JsonResponse({'result': 'success'})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AuthView, self).dispatch(*args, **kwargs)
