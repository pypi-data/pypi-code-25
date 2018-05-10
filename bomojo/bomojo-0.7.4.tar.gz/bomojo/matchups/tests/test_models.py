# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase


class MatchupTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.bob = User.objects.create(username='bob',
                                      email='bob@example.com',
                                      password='top_secret')
        cls.alice = User.objects.create(username='alice',
                                        email='alice@example.com',
                                        password='highly_confidential')

    def test_matchup_populates_slug_on_save(self):
        matchup = self.bob.matchups.create(title='foo vs bar',
                                           movies=['foo', 'bar'])
        self.assertEqual('foo-vs-bar', matchup.slug)

    def test_slug_is_always_unique(self):
        bob_matchup = self.bob.matchups.create(title='foo vs bar',
                                               movies=['foo', 'bar'])
        alice_matchup = self.alice.matchups.create(title='foo vs bar',
                                                   movies=['foo', 'bar'])

        self.assertIn('foo-vs-bar', bob_matchup.slug)
        self.assertIn('foo-vs-bar', alice_matchup.slug)
        self.assertNotEqual(bob_matchup.slug, alice_matchup.slug)

    def test_slug_does_not_change(self):
        matchup = self.bob.matchups.create(title='foo vs bar',
                                           movies=['foo', 'bar'])
        self.assertEqual('foo-vs-bar', matchup.slug)

        matchup.title = 'bar vs foo'
        matchup.save()
        matchup.refresh_from_db()
        self.assertEqual('foo-vs-bar', matchup.slug)
