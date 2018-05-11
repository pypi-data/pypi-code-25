
import socket

if socket.gethostname() == 'arch':
    from djangoforandroid.framework.views import BrythonView as PostHandler
else:
    from djangoforandroid.framework.brython.wsgi_handler import BrythonPostHandler as PostHandler

import json
import os
import socket


########################################################################
class Brython(PostHandler):
    """"""



    #----------------------------------------------------------------------
    def local_ip(self):
        """"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('yeisoncardona.com', 0))
            return s.getsockname()[0]
        except:
            return None