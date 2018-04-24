from django.test import TestCase

from matchups.forms import MatchupForm


class MatchupFormTest(TestCase):
    def test_happy_path(self):
        form = MatchupForm({
            'title': 'foo trilogy',
            'email': 'dan@example.com',
            'description': 'The entire foo trilogy',
            'movies': ['foo', 'bar'],
            'period': '30d'
        })

        self.assertTrue(form.is_valid())

        matchup = form.save()

        self.assertEqual(matchup.title, 'foo trilogy')
        self.assertEqual(matchup.email, 'dan@example.com')
        self.assertEqual(matchup.description, 'The entire foo trilogy')
        self.assertEqual(matchup.movies, ['foo', 'bar'])
        self.assertEqual(matchup.period, '30d')

    def test_minimal_fields(self):
        form = MatchupForm({
            'title': 'foo vs bar',
            'movies': ['foo', 'bar']
        })

        self.assertTrue(form.is_valid())

        matchup = form.save()

        self.assertEqual(matchup.title, 'foo vs bar')
        self.assertEqual(matchup.email, '')
        self.assertEqual(matchup.description, '')
        self.assertEqual(matchup.movies, ['foo', 'bar'])
        self.assertEqual(matchup.period, '')

    def test_title_cannot_be_omitted(self):
        form = MatchupForm({
            'description': 'The entire foo trilogy',
            'movies': ['foo1', 'foo2', 'foo3']
        })

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('required', *form.errors['title'])

    def test_title_cannot_be_blank(self):
        form = MatchupForm({
            'title': '',
            'description': 'The entire foo trilogy',
            'movies': ['foo1', 'foo2', 'foo3']
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('required', *form.errors['title'])

    def test_movies_cannot_be_omitted(self):
        form = MatchupForm({
            'title': 'foo vs bar'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('movies', form.errors)
        self.assertIn('required', *form.errors['movies'])

    def test_movies_cannot_be_empty(self):
        form = MatchupForm({
            'title': 'foo vs bar',
            'movies': []
        })
        self.assertFalse(form.is_valid())
        self.assertIn('movies', form.errors)
        self.assertIn('required', *form.errors['movies'])

    def test_email_must_be_valid_if_provided(self):
        form = MatchupForm({
            'title': 'foo vs bar',
            'email': 'blah',
            'movies': ['foo', 'bar']
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('valid', *form.errors['email'])

    def test_period_must_be_valid_if_provided(self):
        form = MatchupForm({
            'title': 'foo vs bar',
            'movies': ['foo', 'bar'],
            'period': 'blah'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('period', form.errors)
        self.assertIn('valid', *form.errors['period'])
