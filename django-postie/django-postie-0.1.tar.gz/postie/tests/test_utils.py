from django.test import TestCase

from ..utils import get_domain


class GetDomainTestCase(TestCase):
    def test_get_domain(self):
        site_name = get_domain()
        self.assertEqual(site_name, 'example.com')