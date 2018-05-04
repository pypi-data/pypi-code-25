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

from django.core.exceptions import ValidationError

from serialbox.api.viewsets import FormMixin
from serialbox import viewsets

from random_flavorpack.models import RandomizedRegion
from random_flavorpack.api import serializers
from serialbox.errors import RegionBoundaryException


class RandomizedRegionViewSet(viewsets.SerialBoxModelViewSet, FormMixin):
    '''

    # Randomized Region API

    The randomized region API supports the following HTTP actions:

    * GET - Retrieve a region using the `machine_name`
    * POST - Create a region by posting a serialized random region in *JSON*
    or *XML* format.
    * PUT - Update a region by posting a serialized random region in *JSON*
    or *XML* format.
    * DELETE - Delete a region by using the `machine_name` of the region.

    '''
    queryset = RandomizedRegion.objects.all()
    lookup_field = 'machine_name'

    def get_serializer_class(self):
        '''
        Return a different serializer depending on the client request.
        '''
        ret = serializers.RandomizedRegionSerializer
        try:
            if self.request.query_params.get('related') == 'true':
                ret = serializers.RandomizedRegionHyperlinkedSerializer
        except AttributeError:
            pass
        return ret

    def create(self, request, *args, **kwargs):
        try:
            return viewsets.ModelViewSet.create(self, request, *args, **kwargs)
        except ValidationError as v:
            raise RegionBoundaryException(v.detail)


