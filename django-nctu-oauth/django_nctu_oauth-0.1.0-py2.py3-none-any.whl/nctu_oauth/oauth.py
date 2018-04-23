from django.shortcuts import redirect
import requests

OAUTH_URL = 'https://id.nctu.edu.tw'

class OAuth:
    def __init__(self, client_id, client_secret, redirect_url):
        self.grant_type = 'authorization_code'
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url

    def authorize(self):
        request_code = OAUTH_URL + '/o/authorize/?client_id=' + self.client_id + '&scope=profile&response_type=code'
        return redirect(request_code)

    def get_token(self, request, code):
        token_url = OAUTH_URL + '/o/token/'
        data = {
			'grant_type': 'authorization_code',
			'code': code,
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'redirect_uri': self.redirect_url
		}

        result = requests.post(token_url, data=data)
        if result.status_code == 200: # success
            payload = result.json()
            request.session['nctu_token'] = payload.get('access_token')
            request.session['logged_in'] = True
            return True
        else:
            print(result.status_code)
        return False

    @staticmethod
    def get_profile(request):
        if request.session.get('nctu_token', None):
            token = request.session['nctu_token']
            headers = {
                'Authorization': 'Bearer '+token
            }
            request_profile_url = OAUTH_URL + '/api/profile'
            return requests.get(request_profile_url, headers=headers).json()
        return None