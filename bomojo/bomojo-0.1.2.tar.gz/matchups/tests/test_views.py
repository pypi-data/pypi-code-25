# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.test import TestCase

from freezegun import freeze_time

from matchups.models import Matchup


class CreateTestCase(TestCase):
    @freeze_time('2018-03-10 22:17:00')
    def test_happy_path(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar',
            'movies': ['foo', 'bar']
        }), content_type='application/json')

        self.assertEqual(201, response.status_code)
        self.assertEqual(response.json(), {
            'slug': 'foo-vs-bar',
            'title': 'foo vs bar',
            'description': '',
            'avatar': '',
            'movies': ['foo', 'bar'],
            'period': '',
            'created': '2018-03-10T22:17:00+00:00'
        })

        matchup = Matchup.objects.get(slug='foo-vs-bar')
        self.assertEqual('foo vs bar', matchup.title)
        self.assertEqual(['foo', 'bar'], matchup.movies)

        # Ensure fields not supplied are blank.
        self.assertEqual('', matchup.email)
        self.assertEqual('', matchup.description)
        self.assertEqual('', matchup.period)

    @freeze_time('2018-03-10 22:17:00')
    def test_happy_path_all_fields(self):
        response = self.client.post('/matchups/', json.dumps({
            'email': 'dan@example.com',
            'title': 'foo trilogy',
            'description': 'The entire foo trilogy',
            'movies': ['foo', 'foo2', 'foo3'],
            'period': '90d'
        }), content_type='application/json')

        self.assertEqual(201, response.status_code)
        self.assertEqual(response.json(), {
            'slug': 'foo-trilogy',
            'title': 'foo trilogy',
            'avatar': 'https://gravatar.com/avatar/6bf919361414694081de8f80cedba005?size=32&d=retro',
            'description': 'The entire foo trilogy',
            'movies': ['foo', 'foo2', 'foo3'],
            'period': '90d',
            'created': '2018-03-10T22:17:00+00:00'
        })

        matchup = Matchup.objects.get(slug='foo-trilogy')
        self.assertEqual('dan@example.com', matchup.email)
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


class ShowTestCase(TestCase):
    @freeze_time('2018-03-10 22:17:00')
    def test_happy_path(self):
        Matchup.objects.create(title='foo vs bar',
                               description='matchup between foo and bar',
                               movies=['foo', 'bar'],
                               period='30d')
        response = self.client.get('/matchups/foo-vs-bar')
        self.assertEqual(response.json(), {
            'slug': 'foo-vs-bar',
            'title': 'foo vs bar',
            'avatar': '',
            'description': 'matchup between foo and bar',
            'movies': ['foo', 'bar'],
            'period': '30d',
            'created': '2018-03-10T22:17:00+00:00'
        })

    def test_404_for_missing_matchup(self):
        response = self.client.get('/matchups/does-not-exist')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'errors': {
                'slug': ['That matchup does not exist.']
            }
        })


class ListTestCase(TestCase):
    maxDiff = None

    def test_happy_path(self):
        with freeze_time('2018-03-10 22:17:00'):
            Matchup.objects.create(title='foo vs bar',
                                   description='matchup between foo and bar',
                                   movies=['foo', 'bar'],
                                   period='30d')
        with freeze_time('2018-03-10 22:17:01'):
            Matchup.objects.create(title='foo trilogy',
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
                'slug': 'foo-trilogy',
                'title': 'foo trilogy',
                'avatar': '',
                'description': 'all three foo movies',
                'movies': ['foo1', 'foo2', 'foo3'],
                'period': '30d',
                'created': '2018-03-10T22:17:01+00:00'
            },
            {
                'slug': 'foo-vs-bar',
                'title': 'foo vs bar',
                'avatar': '',
                'description': 'matchup between foo and bar',
                'movies': ['foo', 'bar'],
                'period': '30d',
                'created': '2018-03-10T22:17:00+00:00'
            }
        ])
