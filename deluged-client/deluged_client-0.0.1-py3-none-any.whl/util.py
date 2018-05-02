
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details
# http://www.gnu.org/licenses/lgpl-3.0.txt

import os

def findDefaultAccount():
    config = os.environ.get("XDG_CONFIG_HOME")
    auth_path = os.path.join(config, "deluge/auth")

    with open(auth_path, "r") as auth:
        line = auth.readline().split(':')
        return {'user': line[0], 'password': line[1]}

    return {'user': '', 'password': ''}
