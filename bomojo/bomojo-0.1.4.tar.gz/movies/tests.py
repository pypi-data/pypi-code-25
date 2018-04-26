# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache
from django.test import TestCase

from mock import patch


class SearchTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def test_requires_title_param(self):
        response = self.client.get('/movies/search')
        self.assertEqual(response.status_code, 400)

    @patch('pybomojo.search_movies')
    def test_returns_json_response(self, mock):
        mock.return_value = [
            {
                'title': 'Foo',
                'movie_id': 'foo',
                'exact': True
            }
        ]

        response = self.client.get('/movies/search?title=foo')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo',
                    'exact': True
                }
            ]
        })

    @patch('pybomojo.search_movies')
    def test_returns_exact_result_first(self, mock):
        mock.return_value = [
            {
                'title': 'Foo',
                'movie_id': 'foo',
                'exact': False
            },
            {
                'title': 'Foo 2: The Awakening',
                'movie_id': 'foo2',
                'exact': True
            }
        ]

        response = self.client.get('/movies/search/?title=foo%202')
        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Foo 2: The Awakening',
                    'movie_id': 'foo2',
                    'exact': True
                },
                {
                    'title': 'Foo',
                    'movie_id': 'foo',
                    'exact': False
                }
            ]
        })

    @patch('pybomojo.search_movies')
    def test_caches_results(self, mock):
        mock.return_value = []

        response = self.client.get('/movies/search/?title=foo%202')
        self.assertJSONEqual(response.content, {'results': []})

        mock.side_effect = AssertionError(
            'should not have called search_movies again (expected to use '
            'cached result)')

        response = self.client.get('/movies/search/?title=foo%202')
        self.assertJSONEqual(response.content, {'results': []})


class BoxOfficeTestCase(TestCase):
    def setUp(self):
        cache.clear()

    @patch('pybomojo.get_box_office')
    def test_returns_json_response(self, mock):
        mock.return_value = {
            'title': 'Foo 3: ',
            'href': 'http://moviewebsite.com/foo3',
            'box_office': [{
                'day': 'Fri',
                'date': 'Jul. 14 2017',
                'rank': 1,
                'gross': 22100000,
                'theaters': 4022,
                'cumulative': 22100000
            }]
        }

        response = self.client.get('/movies/foo3/boxoffice')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertJSONEqual(response.content, {
            'title': 'Foo 3: ',
            'href': 'http://moviewebsite.com/foo3',
            'box_office': [{
                'day': 'Fri',
                'date': 'Jul. 14 2017',
                'rank': 1,
                'gross': 22100000,
                'theaters': 4022,
                'cumulative': 22100000
            }]
        })

    @patch('pybomojo.get_box_office')
    def test_caches_results(self, mock):
        mock.return_value = {
            'title': 'Bar',
            'href': 'http://moviewebsite.com/bar',
            'box_office': []
        }

        response = self.client.get('/movies/foo3/boxoffice')
        self.assertJSONEqual(response.content, {
            'title': 'Bar',
            'href': 'http://moviewebsite.com/bar',
            'box_office': []
        })

        mock.side_effect = AssertionError(
            'should not have called get_box_office again (expected to use '
            'cached result)')

        response = self.client.get('/movies/foo3/boxoffice')
        self.assertJSONEqual(response.content, {
            'title': 'Bar',
            'href': 'http://moviewebsite.com/bar',
            'box_office': []
        })
