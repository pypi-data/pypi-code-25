import copy
import hashlib
import os
import requests

class Streetviewer(object):

    class_defaults = {
        "height":400,
        "width":600,
        "heading":None,
        "fov":90,
        "pitch":0,
    }

    def __init__(self, key, defaults={}):
        self.key = key
        self.defaults = copy.deepcopy(Streetviewer.class_defaults)
        for k in defaults:
            if defaults.get(k) != None:
                self.defaults[k] = defaults[k]

    def get_picture(self, location, **kwargs):
        params = copy.deepcopy(self.defaults)
        params["key"] = self.key
        for k in kwargs:
            if kwargs.get(k) != None:
                params[k] = kwargs[k]
        params["location"] = location
        url = "https://maps.googleapis.com/maps/api/streetview?size={width}x{height}&location={location}&key={key}&fov={fov}".format(**params)
        for k in ["pitch","heading"]:
            if params.get(k) != None:
                url += "&{}={}".format(k, params[k])
        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError("The request failed ({status_code}): {_content}".format(**vars(response)))
        del params["key"]
        return {
            "params":params,
            "type":response.headers["Content-Type"],
            "body":response._content
        }

    def get_picture_to_file(self, location, filepath, **kwargs):
        info = self.get_picture(location, **kwargs)
        file_hash = hashlib.md5(info["body"]).hexdigest()
        info["hash"] = file_hash
        if os.path.isdir(filepath):
            filepath = os.path.join(filepath, "{}.jpg".format(file_hash))
        with open(filepath, "wb") as f:
            f.write(info["body"])
        return info
