#!/usr/bin/env python
# Copyright 2013 Mingyi Zhang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals





import os
import sys
import traceback
import cam.hacks
from cam.cli import dispatch
from cam.errors import FatalError
from cam.utils import console
def main():
    tb = None
    #exception = None
    try:
        return dispatch(sys.argv[1:])
    except FatalError as exc:
        tb = e.trace
        print("error: %s"%exc.args[0]) 
        return '{0}: {1}'.format(
            exc.__class__.__name__,
            exc.args[0],
        )

    except Exception as exc:
        tb = traceback.format_exc()   
        #exception = exc    
        print("error: %s"%exc.args[0]) 
        return '{0}: {1}'.format(
            exc.__class__.__name__,
            exc.args[0],
        )
    finally:
        if tb is not None:
            
            f = open('cam.~dump','w+')
            f.write(tb)
            #f.write('========     Exception ( %s )    =========\n%s\n'%(type(exception),exception))
            f.close()
            console.log( console.Fore.MAGENTA +'see %s for exception detail.'%os.path.abspath('cam.~dump'))



if __name__ == "__main__":
    sys.exit(main())
