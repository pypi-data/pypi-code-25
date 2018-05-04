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
# Copyright 2018 SerialLab Corp.  All rights reserved.
'''
Contains helper functions that help inspect the local system
with the intent of reporting back settings and capabilities.
'''

from django.conf import settings

def get_asdf():
    '''
    Returns a list of serial-lab specific packages installed on the
    system.
    :return: A list of package names.
    '''
    return settings.INSTALED_APPS
