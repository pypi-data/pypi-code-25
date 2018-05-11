from django.test import TestCase
from django.conf import settings
from django.test.client import RequestFactory

from userservice.test import get_user as get_django_user
from userservice.user import get_user, get_acting_user, get_override_user
from userservice.user import get_original_user, set_override_user
from userservice.user import clear_override, UserService, UserServiceMiddleware


class TestAPI(TestCase):
    def test_basic(self):
        request = RequestFactory().get("/")
        request.session = {}

        self.assertEquals(get_user(request), None)
        self.assertEquals(get_acting_user(request), None)
        self.assertEquals(get_override_user(request), None)
        self.assertEquals(get_original_user(request), None)

    def test_user(self):
        request = RequestFactory().get("/")
        request.session = {}
        request.user = get_django_user('javerage')

        self.assertEquals(get_user(request), 'javerage')
        self.assertEquals(get_acting_user(request), 'javerage')
        self.assertEquals(get_override_user(request), None)
        self.assertEquals(get_original_user(request), 'javerage')

    def test_override(self):
        request = RequestFactory().get("/")
        request.session = {}
        request.user = get_django_user('javerage')

        set_override_user(request, "supportticket")
        self.assertEquals(request.user.username, 'supportticket')
        self.assertEquals(get_user(request), 'supportticket')
        self.assertEquals(get_acting_user(request), 'javerage')
        self.assertEquals(get_override_user(request), 'supportticket')
        self.assertEquals(get_original_user(request), 'javerage')

    def test_clear_override(self):
        request = RequestFactory().get("/")
        request.session = {}
        request.user = get_django_user('javerage')

        set_override_user(request, "supportticket")
        clear_override(request)
        self.assertEquals(request.user.username, 'javerage')

        self.assertEquals(get_user(request), 'javerage')
        self.assertEquals(get_acting_user(request), 'javerage')
        self.assertEquals(get_override_user(request), None)
        self.assertEquals(get_original_user(request), 'javerage')

    def test_legacy(self):
        request = RequestFactory().get("/")
        request.session = {}
        request.user = get_django_user('javerage')

        get_user(request)
        set_override_user(request, "override")

        UserServiceMiddleware().process_request(request)

        self.assertEquals(UserService().get_user(), 'override')
        self.assertEquals(UserService().get_acting_user(), 'javerage')
        self.assertEquals(UserService().get_original_user(), 'javerage')
        self.assertEquals(UserService().get_override_user(), 'override')
        UserServiceMiddleware().process_response(request, None)

    def test_legacy_other_way(self):
        request = RequestFactory().get("/")
        request.session = {}
        request.user = get_django_user('javerage')

        UserServiceMiddleware().process_request(request)

        UserService().set_override_user('o2')

        self.assertEquals(get_user(request), 'o2')
        self.assertEquals(get_acting_user(request), 'javerage')
        self.assertEquals(get_override_user(request), 'o2')
        self.assertEquals(get_original_user(request), 'javerage')
        UserServiceMiddleware().process_response(request, None)
