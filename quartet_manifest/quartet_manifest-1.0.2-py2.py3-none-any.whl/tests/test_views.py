#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_quartet_manifest
------------

Tests for `quartet_manifest` models module.
"""


from django.urls import reverse
from rest_framework.test import APITestCase




class TestQuartet_manifest(APITestCase):

    def setUp(self):
        pass

    def test_manifest(self):
        url = reverse('quartet-manifest')
        response = self.client.get(url, format='xml')
        print(response.content)

    def tearDown(self):
        pass
