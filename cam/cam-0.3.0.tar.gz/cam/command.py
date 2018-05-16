

import os
import glob
import subprocess

from cam.enums import Platform,Architecture
from cam.errors import FatalError
from cam.utils import console

def Exec(script, config,cmd_dir='.',stream=None):
    if script is None:
        return

    if isinstance(script,str):
        console.call( script,cmd_dir,stream)

    elif isinstance(script,dict):
        for key, val in script.items():
            if key == 'python':
                try :
                    exec( val, {
                        'config'   : config,
                        '__file__' : config.__file__
                    })
                except:
                    import traceback
                    print('==================  %s  ================='%__file__)
                    traceback.print_exc()
                    print('=====================================')
                    raise FatalError('exec python script failed')
                    
            elif key in ['ps','powershell']:
                #https://www.pstips.net/powershell-using-scriptblocks.html
                console.call( 'powershell -Command %s'%val,cmd_dir,stream)