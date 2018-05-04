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

import math
import logging
from gettext import gettext as _
from random import shuffle
from serialbox.generators.common import Generator
from random_flavorpack.generators.common import TAPS
from random_flavorpack import random_flavorpack_settings as settings

logger = logging.getLogger(__name__)


class RandomGenerator(Generator):
    '''
    Can be used to return a double-randomized list of numbers if
    shuffle is specified. Otherwise a pseudo-randomized list,
    according to the start value, is generated
    using a standard linear feedback shift register.
    '''

    def generate(self, request, response, region, size, shuffle_numbers=True):
        '''
        Generates the randomized values based on the region supplied.
        '''
        #: :type region: RandomizedRegion
        response.type = 'random'
        numbers, current = self.get_random_numbers(
            region.current or region.start,
            region.min,
            region.max,
            size,
            shuffle_numbers
        )
        region.current = current
        region.remaining = region.remaining - size
        region.save()
        self.set_number_list(response, numbers)

    def get_settings_module(self):
        return settings

    def _enforce_boundaries(self, response, size, region):
        '''
        Makes sure the count does not exceed the amount remaining.
        '''
        remaining_count = region.remaining
        logger.debug('Remaining count for region %s = %s', region,
                     remaining_count)
        if size >= remaining_count:
            logger.debug('Size exceeded remaining count.')
            region.active = False
            response.fulfilled = (size == remaining_count)
            size = remaining_count + 1
            response.size_granted = size
        return size

    def _validate_range(self, start, minimum, maximum):
        if maximum <= minimum:
            raise ValueError(
                _("The maximum can not be less than the minimum."))
        if start < minimum or start > maximum:
            raise ValueError(
                _("The start must be between the minimum and maximum!"))
        rnrange = maximum - minimum
        return rnrange

    def _get_degree(self, maximum, rnrange):
        degree = math.log(rnrange, 2)
        ceiling = math.ceil(degree)
        if degree == ceiling:
            degree += 1
        else:
            degree = ceiling
        if degree > 168:
            raise ValueError(_("Range can not be larger than 63 bits."))
        if degree < 3:
            degree = 3
        return degree

    def _generate_list(self, start, minimum, rnrange, degree):
        yield start
        start -= (minimum - 1)
        init_seed = start
        taps = sum([1 << (tap - 1) for tap in TAPS[degree]])
        while True:
            # use a mask to get the right-most bit
            least_significant_bit = start & 1
            # shift all the bits to the right
            start >>= 1
            if least_significant_bit:
                start ^= taps
            if start == init_seed:
                # the mini- is complete, exit the loop
                raise StopIteration()
            if start <= rnrange:
                yield start + minimum - 1

    def get_random_numbers(self, start, minimum, maximum, size,
                           shuffle_numbers=False):
        rnrange = self._validate_range(start, minimum, maximum)
        # calculate how many bits the register needs to be
        degree = self._get_degree(maximum, rnrange)
        number_gen = self._generate_list(start, minimum, rnrange, degree)
        numbers = [next(number_gen) for x in range(size)]
        current = next(number_gen)
        if shuffle_numbers:
            shuffle(numbers)
        return numbers, current
