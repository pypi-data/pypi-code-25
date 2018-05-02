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

import sys
from random import randint

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from serialbox import models as sb_models
from random_flavorpack.utils import check_randomized_region_boundaries

class RandomizedRegion(sb_models.Region):
    '''
    # RandomizedRegion
    The randomized region defines a region that notes a start value (which
    itself is random) and a minimum and maximim value for any randomized value
    returned from the region.  Multiple randomized regions may be defined per
    pool but their min and max values may not overlap.
    '''
    # TODO Create a field that calculates how many numbers are remaining
    min = models.BigIntegerField(
        verbose_name=_('Minimum'),
        help_text=_('The minimum value in the randomized region.'),
        default=1,
        validators=[MinValueValidator(0)],
        null=False,
        blank=False)
    max = models.BigIntegerField(
        verbose_name=_('Maximum'),
        help_text=_('The maximum value in the randomized region.'),
        default=sys.maxsize,
        validators=[MinValueValidator(0)],
        null=False,
        blank=False)
    start = models.BigIntegerField(
        verbose_name=_('Start Number'),
        validators=[MinValueValidator(0)],
        help_text=_(
            'The start number will fall somewhere in between the '
            'minimum and maximum numbers.  This number will be randomly'
            ' selected by the system to assure the most randomized '
            'range possible'),
        null=True,
        blank=True)
    current = models.BigIntegerField(
        verbose_name=_('Current'),
        help_text=_('The current number represents the next number in the '
                    'generator.  The current number is used by the system as '
                    'a state variable that, along with the start, '
                    'can be used to re-position the random number generator '
                    'where it left off.'),
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    remaining = models.BigIntegerField(
        verbose_name=_('Remaining'),
        help_text=_('The number of remaining serial numbers in this randomized '
                    'region.'),
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        '''
        Return the human readable name for any interface elements.
        '''
        return self.readable_name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.id:
            self.start = self.start or randint(self.min, self.max)
            self.current = self.current or self.start
            self.remaining = self.remaining or self.max - self.min
            self._establish_order()

        check_randomized_region_boundaries(self)
        sb_models.Region.save(
            self,
            force_insert,
            force_update,
            using,
            update_fields)

    def clean(self):
        check_randomized_region_boundaries(self)

    def _establish_order(self):
        '''
        Establish order where there is none. :-)
        '''
        regions = RandomizedRegion.objects.filter(pool=self.pool).aggregate(
            models.Max('order')
        )
        val = regions['order__max'] or 0 + 1
        self.order = val + 1

    class Meta(object):
        app_label = 'serialbox'
        verbose_name = _('Randomized Region')
        verbose_name_plural = _('Randomized Regions')
