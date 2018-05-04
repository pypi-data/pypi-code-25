# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2015 Rob Magee.  All rights reserved.

from rest_framework.routers import DefaultRouter
from random_flavorpack.api.viewsets import RandomizedRegionViewSet



router = DefaultRouter()
router.register(r'randomized-regions', RandomizedRegionViewSet,
                base_name='randomized-regions')
urlpatterns = router.urls
