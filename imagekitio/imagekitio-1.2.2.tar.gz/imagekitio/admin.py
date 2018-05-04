''' This module have delete and purge file functions '''

from __future__ import absolute_import

import time
from imagekitio import utils
import requests


class Admin(object):
    ''' Admin class '''
    def __init__(self, path=None, globl=None):
        self.path = path
        self.files = {'image': ''}

        if utils.PY3:
            self.options = dict({'path' : path}, **globl)
        else:
            self.options = dict({'path' : path} + globl.items() )

        self.options["timestamp"] = int(time.time())

        if not self.path:
            raise utils.Error("Invalid or missing upload parameters - %d - %s" % (2400, "BAD_REQUEST"))

        


    def delete_file(self):
        ''' Delete file post request '''

        url = utils.get_protocol(False) + '//' + utils.get_image_delete_api()
        signature = utils.calculate_delete_signature(self.options)

        form_data = {
            'path': self.options['path'],
            'imagekitId': self.options['imagekit_id'],
            'signature': signature
        }
        result = requests.post(url, data=form_data)
        return result


    def purge_file(self):
        ''' Purge file post request '''

        url = utils.get_protocol(False) + '//' + utils.get_image_purge_api()
        signature = utils.calculate_purge_signature(self.options)
        form_data = {
            'url': self.options['path'],
            'imagekitId': self.options['imagekit_id'],
            'signature': signature
        }

        result = requests.post(url, data=form_data)
        return result
