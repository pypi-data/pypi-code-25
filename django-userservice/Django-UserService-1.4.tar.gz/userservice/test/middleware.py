from django.test import TestCase
from django.conf import settings
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from userservice.user import UserServiceMiddleware, UserService
from userservice.user import UninitializedError
from userservice.test import get_user

class TestMiddleware(TestCase):
    def test_basic(self):
        """
        Test that we do the right thing with no user in session
        """
        middleware = UserServiceMiddleware()
        request = RequestFactory().get("/")
        request.session = {}

        with self.settings(DEBUG=True):
            middleware.process_request(request)
            self.assertEquals(UserService().get_user(), None)
            middleware.process_response(request, None)

        with self.settings(DEBUG=False):
            middleware.process_request(request)
            self.assertEquals(UserService().get_user(), None)
            middleware.process_response(request, None)


    def test_user(self):
        middleware = UserServiceMiddleware()
        request = RequestFactory().get("/")
        request.session = {}
        request.user = get_user('javerage')

        with self.settings(DEBUG=True):
            middleware.process_request(request)
            self.assertEquals(UserService().get_user(), 'javerage')
            self.assertEquals(UserService().get_acting_user(), 'javerage')
            self.assertEquals(UserService().get_original_user(), 'javerage')
            self.assertEquals(UserService().get_override_user(), None)
            middleware.process_response(request, None)

        with self.settings(DEBUG=False):
            middleware.process_request(request)
            self.assertEquals(UserService().get_user(), 'javerage')
            self.assertEquals(UserService().get_acting_user(), 'javerage')
            self.assertEquals(UserService().get_original_user(), 'javerage')
            self.assertEquals(UserService().get_override_user(), None)
            middleware.process_response(request, None)

    def test_override(self):
        middleware = UserServiceMiddleware()
        request = RequestFactory().get("/")
        request.session = {}
        request.user = get_user('javerage')

        with self.settings(DEBUG=True):
            middleware.process_request(request)
            UserService().set_override_user('supportticket')
            self.assertEquals(UserService().get_user(), 'supportticket')
            self.assertEquals(UserService().get_acting_user(), 'javerage')
            self.assertEquals(UserService().get_original_user(), 'javerage')
            self.assertEquals(UserService().get_override_user(), 'supportticket')

            UserService().clear_override()
            self.assertEquals(UserService().get_user(), 'javerage')
            self.assertEquals(UserService().get_acting_user(), 'javerage')
            self.assertEquals(UserService().get_original_user(), 'javerage')
            self.assertEquals(UserService().get_override_user(), None)
            middleware.process_response(request, None)

        with self.settings(DEBUG=False):
            middleware.process_request(request)
            UserService().set_override_user('supportticket')
            self.assertEquals(UserService().get_user(), 'supportticket')
            self.assertEquals(UserService().get_acting_user(), 'javerage')
            self.assertEquals(UserService().get_original_user(), 'javerage')
            self.assertEquals(UserService().get_override_user(), 'supportticket')

            UserService().clear_override()
            self.assertEquals(UserService().get_user(), 'javerage')
            self.assertEquals(UserService().get_acting_user(), 'javerage')
            self.assertEquals(UserService().get_original_user(), 'javerage')
            self.assertEquals(UserService().get_override_user(), None)
            middleware.process_response(request, None)

    def test_django_1_10_style(self):
        with self.settings(DEBUG=True):
            request = RequestFactory().get(reverse("userservice_override"))
            request.session = {}
            request.user = get_user('javerage')

            def get_response(*args, **kwargs):
                UserService().set_override_user('supportticket')
                self.assertEquals(UserService().get_user(), 'supportticket')
                self.assertEquals(UserService().get_acting_user(), 'javerage')
                self.assertEquals(UserService().get_original_user(), 'javerage')
                self.assertEquals(UserService().get_override_user(), 'supportticket')

                UserService().clear_override()
                self.assertEquals(UserService().get_user(), 'javerage')
                self.assertEquals(UserService().get_acting_user(), 'javerage')
                self.assertEquals(UserService().get_original_user(), 'javerage')
                self.assertEquals(UserService().get_override_user(), None)

                return request

            middleware = UserServiceMiddleware(get_response=get_response)

            with self.assertRaises(UninitializedError):
                UserService().get_user()
            response = middleware(request)
            with self.assertRaises(UninitializedError):
                UserService().get_user()

