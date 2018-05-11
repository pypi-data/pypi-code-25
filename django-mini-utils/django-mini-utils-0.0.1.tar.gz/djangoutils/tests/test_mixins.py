from django.views.generic import DetailView
from django.test import TestCase
from django.test.client import RequestFactory

from djangoutils.mixins import GetArgMixin

# Create your tests here.


class TestView(DetailView, GetArgMixin):

    def get(self, request, *args, **kwargs):
        abc = self.get_argument('abc', _type=int)
        assert abc == 1


class MixinsTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/?abc=1')
        setattr(self.request, 'data', {})
        setattr(self.request, 'query_params', {'abc': '1'})

    def test_get_args(self):
        view = TestView.as_view()
        view(self.request)
