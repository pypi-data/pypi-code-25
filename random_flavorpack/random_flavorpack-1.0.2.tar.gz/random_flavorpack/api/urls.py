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

from django.conf.urls import url

from random_flavorpack.api import viewsets
from random_flavorpack.api.routers import router

urlpatterns = router.urls

# urlpatterns = [
#     url(r'^randomized-regions/$',
#         viewsets.randomized_region_list,
#         name='randomized-region-list'),
#     url(r'^randomized-region-create/$',
#         viewsets.randomized_region_create,
#         name='randomized-region-create'),
#     url(r'^randomized-region-detail/(?P<machine_name>[0-9a-zA-Z]{1,100})/$',
#         viewsets.randomized_region_detail,
#         name='randomized-region-detail'),
#     url(r'^randomized-region-modify/(?P<machine_name>[0-9a-zA-Z]{1,100})/$',
#         viewsets.randomized_region_modify,
#         name='randomized-region-modify'),
#     url(r'^randomized-region-form/(?P<machine_name>[0-9a-zA-Z]{1,100})/$',
#         viewsets.randomized_region_form,
#         name='randomized-region-form'),
# ]
