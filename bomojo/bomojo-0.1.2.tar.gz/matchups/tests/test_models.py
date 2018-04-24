# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from matchups.models import Matchup


class MatchupTestCase(TestCase):
    def test_matchup_populates_slug_on_save(self):
        matchup = Matchup.objects.create(title='foo vs bar',
                                         movies=['foo', 'bar'])
        self.assertEqual('foo-vs-bar', matchup.slug)

    def test_slug_is_always_unique(self):
        bob_matchup = Matchup.objects.create(email='bob@example.com',
                                             title='foo vs bar',
                                             movies=['foo', 'bar'])
        alice_matchup = Matchup.objects.create(email='alice@example.com',
                                               title='foo vs bar',
                                               movies=['foo', 'bar'])

        self.assertIn('foo-vs-bar', bob_matchup.slug)
        self.assertIn('foo-vs-bar', alice_matchup.slug)
        self.assertNotEqual(bob_matchup.slug, alice_matchup.slug)

    def test_slug_does_not_change(self):
        matchup = Matchup.objects.create(title='foo vs bar',
                                         movies=['foo', 'bar'])
        self.assertEqual('foo-vs-bar', matchup.slug)

        matchup.title = 'bar vs foo'
        matchup.save()
        matchup.refresh_from_db()
        self.assertEqual('foo-vs-bar', matchup.slug)
