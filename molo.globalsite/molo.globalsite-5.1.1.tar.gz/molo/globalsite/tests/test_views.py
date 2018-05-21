import pytest
from django.test import TestCase, Client
from django.http.request import HttpRequest
from django.core.urlresolvers import reverse
from wagtail.wagtailcore.models import Site
from molo.core.tests.base import MoloTestCaseMixin
from molo.globalsite.models import CountrySite, GlobalSiteSettings, Region
from molo.globalsite import geo


@pytest.mark.django_db
class TestGlobalSiteViews(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.request = HttpRequest()
        self.mk_main()
        self.mk_main2()

        africa = Region.objects.create(name='Africa')
        asia = Region.objects.create(name='Asia')

        CountrySite.objects.create(
            name='South Africa', code='za',
            site_url='http://za.site.org', region=africa)
        CountrySite.objects.create(
            name='Iran', code='IR',
            site_url='http://ir.site.org', region=asia)

        default_site = Site.objects.get(is_default_site=True)
        self.setting = GlobalSiteSettings.objects.create(site=default_site)
        self.setting.is_globalsite = True
        self.setting.description = 'Welcome To Global Site'
        self.setting.save()

    def test_country_sites(self):
        country = CountrySite.objects.all()
        self.assertEquals(country.count(), 2)
        self.assertEquals(country[0].code, 'ZA')
        self.assertEquals(country[0].name, 'South Africa')
        self.assertEquals(country[1].code, 'IR')
        self.assertEquals(country[1].name, 'Iran')

    def test_global_site_is_activated(self):
        response = self.client.get('/')
        self.assertRedirects(
            response, reverse('molo.globalsite:country_selection'))
        self.setting.is_globalsite = False
        self.setting.save()
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_country_listing(self):
        response = self.client.get('/', follow=True)
        self.assertContains(response, 'Welcome To Global Site')
        self.assertContains(response, 'Africa')
        self.assertContains(response, 'South Africa')
        self.assertContains(response, 'Asia')
        self.assertContains(response, 'Iran')

    def test_country_redirect(self):
            response = self.client.get(
                reverse('molo.globalsite:set_country', args=('ZA',)))
            self.assertEquals(response.url, 'http://za.site.org')

    def test_auto_redirect(self):
        self.client.get(
            reverse('molo.globalsite:set_country', args=('ZA',)))
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.client.get(
            reverse('molo.globalsite:set_country', args=('ZA',)))
        self.setting.autoredirect = True
        self.setting.save()
        response = self.client.get('/')
        self.assertEquals(response.status_code, 302)

    def test_changing_country(self):
        with self.settings(GLOBAL_SITE_URL=self.site.root_url):
            client = Client(HTTP_HOST=self.site2.hostname)
            url = self.site2.root_url + '/globalsite/changecountry/'
            response = client.get(url)
            self.assertEquals(
                response.url,
                'http://main-1.localhost:8000/globalsite/countries/')
            response = client.get(url, follow=True)
            self.assertContains(response, 'South Africa')

    def test_settings_globalsite_ignore_path(self):
        excl = ['/search/']
        response = self.client.get(excl[0])
        self.assertEquals(response.status_code, 302)
        with self.settings(GLOBAL_SITE_IGNORE_PATH=excl):
            response = self.client.get(excl[0])
            self.assertEquals(response.status_code, 200)

    def test_country_detection_using_ip(self):
        self.request.META['HTTP_X_FORWARDED_FOR'] = '41.31.255.255'
        self.assertEqual(geo.get_country_code(
            self.request), 'ZA')
        self.assertEqual(geo.get_country_site(
            self.request), 'http://za.site.org')

        self.request.META['HTTP_X_FORWARDED_FOR'] = '146.185.25.250'
        self.assertEqual(geo.get_country_code(
            self.request), 'GB')
        self.assertEqual(geo.get_country_site(
            self.request), None)

        self.request.META['HTTP_X_FORWARDED_FOR'] = 'http://127.0.0.1'
        self.assertEqual(geo.get_country_code(
            self.request), None)
        self.assertEqual(geo.get_country_site(
            self.request), None)

    def test_geolocation_using_ip(self):
        client = Client(HTTP_X_FORWARDED_FOR='41.31.255.255')
        response = client.get('/')
        self.assertRedirects(
            response, reverse('molo.globalsite:country_selection'))

        self.setting.geolocation = True
        self.setting.save()
        response = client.get('/')
        self.assertEquals(response.url, 'http://za.site.org')
