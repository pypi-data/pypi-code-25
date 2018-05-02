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

from rest_framework import serializers

from serialbox import models as pool_models
from serialbox.api.serializers import RegionSerializer
# from serialbox.api import serializers as sb_serializers

from random_flavorpack import models as fp_models

##
# These fields will be added to the pool serializer automatically since
# they are specified in the pool_slug_fields and the pool_hyperlinked_fields
# values in the random_flavorpack.apps.RandomFlavorpackConfig module.
##
randomizedregion_set = serializers.SlugRelatedField(
    many=True,
    queryset=fp_models.RandomizedRegion.objects.all(),
    slug_field='machine_name',
    required=False
)

randomizedregion_hyperlink_set = serializers.HyperlinkedRelatedField(
    many=True,
    read_only=True,
    view_name='randomized-regions-detail',
    lookup_field='machine_name',
)


class RandomizedRegionSerializer(RegionSerializer):
    '''
    Adds slug relation to the randomized Region for pools using the
    machine_name field as the value and also
    excludes the primary key since it is meaningless for clients.
    '''
    class Meta(object):
        model = fp_models.RandomizedRegion
        exclude = ('id', )


class RandomizedRegionHyperlinkedSerializer(RandomizedRegionSerializer):
    '''
    Adds URL relation to the randomized Region for pools and also
    excludes the primary key since it is meaningless for clients.
    '''
    pool = serializers.HyperlinkedRelatedField(view_name='pool-detail',
                                               read_only=True,
                                               lookup_field='machine_name')
