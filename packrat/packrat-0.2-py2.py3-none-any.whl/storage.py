from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
import hashlib
import requests


class PackratFile(object):
    def __init__(self, md5, base_url):
        self.md5 = md5
        self.base_url = base_url
        super().__init__()

    def url(self):
        return "{}/md5/{}".format(self.base_url, self.md5)

    def read(self, *args, **kwargs):
        response = requests.get(self.url())
        return response.read(*args, **kwargs)


@deconstructible
class PackratStorage(Storage):

    def __init__(self, base_url='http://localhost/'):
        super().__init__()
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        return PackratFile(md5=name, base_url=self.base_url)

    def _save(self, name, content):
        # Just compute the MD5, and that's the name. We assume it's already
        # been uploaded.
        # FIXME Read in chunks
        md5 = hashlib.md5(content.read())
        return md5.hexdigest()

    def exists(self, name):
        # We don't use names, so all names are available!
        return False

    def url(self, name):
        return PackratFile(md5=name, base_url=self.base_url).url()
