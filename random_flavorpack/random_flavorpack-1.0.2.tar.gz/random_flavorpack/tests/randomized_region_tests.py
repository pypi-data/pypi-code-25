'''
    Copyright 2018 SerialLab, CORP

    This file is part of RandomFlavorpack.

    RandomFlavorpack is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RandomFlavorpack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with RandomFlavorpack.  If not, see <http://www.gnu.org/licenses/>.
'''

from django.contrib.auth.models import User
from django.urls import reverse
from django.core.management import call_command

call_command('makemigrations', interactive=False)
import collections
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status

from serialbox.utils import get_region_by_machine_name

from random_flavorpack.generators.random import RandomGenerator

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('random_unit_tests')


class RandomTests(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser',
                                        password='unittest',
                                        email='testuser@seriallab.local')
        self.logging_setup()
        self.client.force_authenticate(user=user)
        self.create_pool()
        self.create_region()

    def logging_setup(self):
        import logging
        import sys

        root = logging.getLogger()
        root.setLevel(logging.INFO)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def create_pool(self, data=None, assert_status=status.HTTP_201_CREATED):
        '''
        Ensure we can create a new pool instance.
        '''
        data = data or {
            "readable_name": "Random Unit Test Pool",
            "machine_name": "rutpool1",
            "active": "true",
            "request_threshold": 100
        }
        url = reverse('pool-create')
        response = self.client.post(url, data, format='json')
        logger.info(response.content)
        self.assertEqual(response.status_code, assert_status)

    def create_region(self, data=None, assert_status=status.HTTP_201_CREATED):
        '''
        Ensure we can create a test region for the created pool instance
        '''
        data = data or {
            "pool": "rutpool1",
            "readable_name": "Unit Test Random Region",
            "machine_name": "utrr",
            "active": True,
            "min": 100000,
            "max": 10000000,
            "start": 1000001,
            "current": 1000001
        }
        url = reverse('randomized-regions-list')
        response = self.client.post(url, data, format='json')
        logger.info(response.content)
        self.assertEqual(response.status_code, assert_status)
        return response

    def test_create_region_bad_start(self, data=None,
                                     assert_status=status.HTTP_201_CREATED):
        '''
        Ensure we can create a test region for the created pool instance
        '''
        data = data or {
            "pool": "rutpool1",
            "readable_name": "Bad Unit Test Random Region",
            "machine_name": "utrr2",
            "active": True,
            "min": 1,
            "max": 100,
            "start": 1000001,
            "current": 1000001
        }
        url = reverse('randomized-regions-list')
        response = self.client.post(url, data, format='json')
        logger.info(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        return response

    def test_create_region_bad_min(self, data=None, \
                                   assert_status=status.HTTP_201_CREATED):
        '''
        Ensure we can create a test region for the created pool instance
        '''
        data = data or {
            "pool": "rutpool1",
            "readable_name": "Bad Unit Test Random Region",
            "machine_name": "utrr2",
            "active": True,
            "min": 122222222,
            "max": 10000000,
            "start": 1000001,
            "current": 1000001
        }
        url = reverse('randomized-regions-list')
        response = self.client.post(url, data, format='json')
        logger.info(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        return response

    def test_allocate_numbers(self):
        '''
        Ensure we can get numbers from the pool
        '''
        url = reverse('allocate-numbers', args=['rutpool1', '10'])
        response = self.client.get(url, format='json')
        logger.info(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_region_remaining(self):
        region = get_region_by_machine_name('utrr')
        self.assertEqual(region.remaining, (region.max - region.min),
                         'The region remaining size has not been calculated  '
                         'correctly')

    def test_get_region_by_machine_name(self):
        region = get_region_by_machine_name('utrr')
        self.assertTrue(
            region is not None,
            'Could not look up region %s using '
            'the get_region_by_machine_name utility.')
        logger.info('randomized region was retrieved...')

    def test_generate_10_pseudo_random(self):
        state = 23423
        rg = RandomGenerator()
        numbers = \
            rg.get_random_numbers(state, 1, 999999999999,
                                  size=10, shuffle_numbers=False)[0]
        logger.info(numbers)
        self.assertTrue(
            set(numbers) == {23423, 687196089791, 927714708335, 876175001015,
                             850405147355, 837520220525,
                             831077757110, 415538878555, 620087086125,
                             997239621142})

    def test_shuffle(self):
        state = 23423
        rg = RandomGenerator()
        numbers = rg.get_random_numbers(state, 1, 999999999999, size=10,
                                        shuffle_numbers=True)[0]
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        orig = [23423, 687196089791, 927714708335, 876175001015,
                850405147355, 837520220525,
                831077757110, 415538878555, 620087086125,
                997239621142]
        self.assertFalse(orig[1] == numbers[1] and orig[2] == numbers[2] and
                         orig[3] == orig[3] and orig[4] == orig[4] and
                         orig[5] == orig[5] and
                         orig[6] == orig[6] and
                         orig[7] == orig[7] and
                         orig[8] == orig[8] and
                         orig[9] == orig[9],
                         'The list has not been shuffled')

    def test_get_regions(self):
        factory = APIRequestFactory()
        ret = factory.get('/randomized-regions/')
        print(ret)
