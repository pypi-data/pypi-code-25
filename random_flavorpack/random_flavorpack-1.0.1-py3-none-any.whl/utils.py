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

from serialbox.errors import RegionBoundaryException

def check_randomized_region_boundaries(randomized_region):
    # type: (RandomizedRegion) -> None
    '''
    Checks the pool of a given randomized region to ensure that no
    two regions have overlapping numbers.

    :param randomized_region: The region to check
    :return: None or will raise a RegionsBoundaryException
    '''
    if randomized_region.min >= randomized_region.max:
        raise RegionBoundaryException(
            'The random region has a malformed boundary.  '
            'The min value may not be greater than '
            'or equal to the the max value.')
    if randomized_region.start > randomized_region.max or \
        randomized_region.start < randomized_region.min:
        raise RegionBoundaryException(
            'The random region may not hav a start value less than '
            'it\'s min value or greater than it\'s max.')
