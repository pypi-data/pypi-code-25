import unittest
from nctu_oauth.oauth import OAuth
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings
import django, os
from unittest import mock

os.environ["DJANGO_SETTINGS_MODULE"] = "test.settings"

django.setup()

rf = RequestFactory()

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://id.nctu.edu.tw/api/profile':
        return MockResponse({'success': True}, 200)
    elif args[0] == 'https://id.nctu.edu.tw/o/token/':
        return MockResponse({'access_token': '123456'}, 200)

    return MockResponse(None, 404)


class TestOAuthClass(unittest.TestCase):

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_profile(self, mock_get):
        get_request = rf.get(path='/oauth',HTTP_HOST='docs.djangoproject.dev:8000')
        middleware = SessionMiddleware()
        middleware.process_request(get_request)
        get_request.session.save()
        get_request.session['nctu_token'] = '123456'
        result = OAuth.get_profile(get_request)
        self.assertEqual(result['success'], True)

    @mock.patch('requests.post', side_effect=mocked_requests_get)
    def test_get_token(self, mock_get):
        oauth = OAuth('123456', 'client-secret-123456', 'redirect-url')
        request = rf.get(path='/oauth',HTTP_HOST='docs.djangoproject.dev:8000')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        success_result = oauth.get_token(request, 'nctu-oauth-token')
        self.assertEqual(success_result, True)


if __name__ == '__main__':
    unittest.main()