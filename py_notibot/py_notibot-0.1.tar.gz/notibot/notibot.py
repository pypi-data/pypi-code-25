from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import requests

_DEFAULT_HOST_URL = "http://128.199.123.244:8080/notibot"


class Notibot(object):
    __send_url = "{}/send"
    __send_image_url = "{}/send_image"

    def __init__(self, token):
        self.__token = token

        self.__send_method = None
        self.__send_image_method = None

        self.set_host_url(_DEFAULT_HOST_URL)

    def set_host_url(self, host_url):
        self.__send_method = Notibot.__send_url.format(host_url)
        self.__send_image_method = Notibot.__send_image_url.format(host_url)

    def send(self, text):
        params = {"project_token": self.__token, "text": text}
        response = requests.post(self.__send_method, params=params)
        return response.status_code == 200

    def send_image(self, image_path, caption=None):
        """
        This method can produce ResourceWarning.
        """
        params = {"project_token": self.__token, "caption": ""}
        if caption is not None:
            params["caption"] = caption

        with open(image_path, "rb") as image_file:
            filename = os.path.basename(image_path)
            _, image_ext = os.path.splitext(image_path)
            files = {"file": (filename, image_file, "image/{}".format(image_ext[1:]))}

            response = requests.post(self.__send_image_method, params=params, files=files)
            return response.status_code == 200
