# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.models import User
from django.test import TestCase

from freezegun import freeze_time

from bomojo.matchups.models import Matchup
from bomojo.utils import get_avatar_url


class CreateTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='joe',
                                       email='joe@example.com',
                                       password='top_secret')
        cls.avatar_url = get_avatar_url(cls.user.email)

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    @freeze_time('2018-03-10 22:17:00')
    def test_happy_path(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar',
            'movies': ['foo', 'bar']
        }), content_type='application/json')

        self.assertEqual(201, response.status_code)
        self.assertEqual(response.json(), {
            'creator': {
                'username': 'joe',
                'avatar': self.avatar_url
            },
            'slug': 'foo-vs-bar',
            'title': 'foo vs bar',
            'description': '',
            'movies': ['foo', 'bar'],
            'period': '',
            'created': '2018-03-10T22:17:00+00:00',
            'updated': '2018-03-10T22:17:00+00:00'
        })

        matchup = Matchup.objects.get(slug='foo-vs-bar')
        self.assertEqual('foo vs bar', matchup.title)
        self.assertEqual(['foo', 'bar'], matchup.movies)

        # Ensure fields not supplied are blank.
        self.assertEqual('', matchup.description)
        self.assertEqual('', matchup.period)

    @freeze_time('2018-03-10 22:17:00')
    def test_happy_path_all_fields(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo trilogy',
            'description': 'The entire foo trilogy',
            'movies': ['foo', 'foo2', 'foo3'],
            'period': '90d'
        }), content_type='application/json')

        self.assertEqual(201, response.status_code)
        self.assertEqual(response.json(), {
            'creator': {
                'username': 'joe',
                'avatar': self.avatar_url
            },
            'slug': 'foo-trilogy',
            'title': 'foo trilogy',
            'description': 'The entire foo trilogy',
            'movies': ['foo', 'foo2', 'foo3'],
            'period': '90d',
            'created': '2018-03-10T22:17:00+00:00',
            'updated': '2018-03-10T22:17:00+00:00'
        })

        matchup = Matchup.objects.get(slug='foo-trilogy')
        self.assertEqual('foo trilogy', matchup.title)
        self.assertEqual('The entire foo trilogy', matchup.description)
        self.assertEqual(['foo', 'foo2', 'foo3'], matchup.movies)
        self.assertEqual('90d', matchup.period)

    def test_requires_title_param(self):
        response = self.client.post('/matchups/', json.dumps({
            'movies': ['foo', 'bar']
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'errors': {
                'title': ['This field is required.']
            }
        })

    def test_title_cannot_be_blank(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': '',
            'movies': ['foo', 'bar']
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'errors': {
                'title': ['This field is required.']
            }
        })

    def test_requires_movies_param(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'errors': {
                'movies': ['This field is required.']
            }
        })

    def test_movies_cannot_be_empty(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar',
            'movies': []
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'errors': {
                'movies': ['This field is required.']
            }
        })

    def test_401_for_unauthenticated_attempt(self):
        self.client.logout()
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar',
            'movies': ['foo', 'bar']
        }), content_type='application/json')

        self.assertEqual(401, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'creator': ['You must log in to create a matchup.']
            }
        })


class ShowTestCase(TestCase):
    @freeze_time('2018-03-10 22:17:00')
    def test_happy_path(self):
        user = User.objects.create(username='joe',
                                   email='joe@example.com',
                                   password='top_secret')

        user.matchups.create(title='foo vs bar',
                             description='matchup between foo and bar',
                             movies=['foo', 'bar'],
                             period='30d')
        response = self.client.get('/matchups/foo-vs-bar')
        self.assertEqual(response.json(), {
            'creator': {
                'username': 'joe',
                'avatar': get_avatar_url(user.email)
            },
            'slug': 'foo-vs-bar',
            'title': 'foo vs bar',
            'description': 'matchup between foo and bar',
            'movies': ['foo', 'bar'],
            'period': '30d',
            'created': '2018-03-10T22:17:00+00:00',
            'updated': '2018-03-10T22:17:00+00:00'
        })

    def test_404_for_missing_matchup(self):
        response = self.client.get('/matchups/does-not-exist')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'errors': {
                'slug': ['That matchup does not exist.']
            }
        })


class UpdateTestCase(TestCase):
    def test_happy_path(self):
        user = User.objects.create(username='joe',
                                   email='joe@example.com',
                                   password='top_secret')

        with freeze_time('2018-04-28 16:14:00'):
            user.matchups.create(title='foo vs bar',
                                 description='matchup between foo and bar',
                                 movies=['foo', 'bar'],
                                 period='30d')

        self.client.force_login(user)
        with freeze_time('2018-04-28 16:14:01'):
            response = self.client.put('/matchups/foo-vs-bar', json.dumps({
                'title': 'updated title',
                'description': 'updated description'
            }), content_type='application/json')

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json(), {
            'creator': {
                'username': 'joe',
                'avatar': get_avatar_url(user.email)
            },
            'slug': 'foo-vs-bar',
            'title': 'updated title',
            'description': 'updated description',
            'movies': ['foo', 'bar'],
            'period': '30d',
            'created': '2018-04-28T16:14:00+00:00',
            'updated': '2018-04-28T16:14:01+00:00'
        })

    def test_404_for_missing_matchup(self):
        user = User.objects.create(username='joe',
                                   email='joe@example.com',
                                   password='top_secret')

        self.client.force_login(user)
        response = self.client.put('/matchups/foo-vs-bar', json.dumps({
            'title': 'updated title',
            'description': 'updated description'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'errors': {
                'slug': ['That matchup does not exist.']
            }
        })

    def test_redirect_for_unauthenticated_attempt(self):
        user = User.objects.create(username='joe',
                                   email='joe@example.com',
                                   password='top_secret')

        user.matchups.create(title='foo vs bar',
                             description='matchup between foo and bar',
                             movies=['foo', 'bar'],
                             period='30d')

        response = self.client.put('/matchups/foo-vs-bar', json.dumps({
            'title': 'updated title',
            'description': 'updated description'
        }), content_type='application/json')

        self.assertEqual(401, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'creator': ['You must log in to edit your matchups.']
            }
        })

    def test_403_for_unauthorized_attempt(self):
        bob = User.objects.create(username='bob',
                                  email='bob@example.com',
                                  password='top_secret')

        bob.matchups.create(title='foo vs bar',
                            description='matchup between foo and bar',
                            movies=['foo', 'bar'],
                            period='30d')

        alice = User.objects.create(username='alice',
                                    email='alice@example.com',
                                    password='highly_confidential')

        self.client.force_login(alice)
        response = self.client.put('/matchups/foo-vs-bar', json.dumps({
            'title': 'updated title',
            'description': 'updated description'
        }), content_type='application/json')

        self.assertEqual(403, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'creator': ["You cannot edit other people's matchups."]
            }
        })


class ListTestCase(TestCase):
    def test_happy_path(self):
        user = User.objects.create(username='joe',
                                   email='joe@example.com',
                                   password='top_secret')

        avatar_url = get_avatar_url(user.email)

        with freeze_time('2018-03-10 22:17:00'):
            user.matchups.create(title='foo vs bar',
                                 description='matchup between foo and bar',
                                 movies=['foo', 'bar'],
                                 period='30d')
        with freeze_time('2018-03-10 22:17:01'):
            user.matchups.create(title='foo trilogy',
                                 description='all three foo movies',
                                 movies=['foo1', 'foo2', 'foo3'],
                                 period='30d')

        # Initially, no matchups should be returned since none are featured.
        response = self.client.get('/matchups/')
        self.assertEqual(response.json(), [])

        Matchup.objects.all().update(featured=True)

        # Now that they're featured, both matchups should be returned.
        response = self.client.get('/matchups/')
        self.assertEqual(response.json(), [
            {
                'creator': {
                    'username': 'joe',
                    'avatar': avatar_url
                },
                'slug': 'foo-trilogy',
                'title': 'foo trilogy',
                'description': 'all three foo movies',
                'movies': ['foo1', 'foo2', 'foo3'],
                'period': '30d',
                'created': '2018-03-10T22:17:01+00:00',
                'updated': '2018-03-10T22:17:01+00:00'
            },
            {
                'creator': {
                    'username': 'joe',
                    'avatar': avatar_url
                },
                'slug': 'foo-vs-bar',
                'title': 'foo vs bar',
                'description': 'matchup between foo and bar',
                'movies': ['foo', 'bar'],
                'period': '30d',
                'created': '2018-03-10T22:17:00+00:00',
                'updated': '2018-03-10T22:17:00+00:00'
            }
        ])
