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

from django.utils.translation import gettext_lazy as _

from serialbox.flavor_packs import FlavorPackApp


class RandomFlavorpackConfig(FlavorPackApp):
    name = "random_flavorpack"
    verbose_name = _("Random FlavorPack")

    # This field tells the PoolSerializerMeta class to add this field
    # to the pool serializer so that randomized regions auto-magically show up
    # in the pool serializer output.
    @property
    def pool_slug_fields(self):
        return {
            'randomizedregion_set':
            'random_flavorpack.api.serializers.randomizedregion_set'
        }

    # Each flavorpack must supply hyperlink fields for it's serializer fields
    @property
    def pool_hyperlink_fields(self):
        return {
            'randomizedregion_set':
            'random_flavorpack.api.serializers.randomizedregion_hyperlink_set'
        }
    # Each flavorpack must supply number generators for it's regions

    @property
    def generators(self):
        return {
            'random_flavorpack.models.RandomizedRegion':
            'random_flavorpack.generators.random.RandomGenerator'
        }

    @property
    def api_urls(self):
        return ['randomized-regions-list']