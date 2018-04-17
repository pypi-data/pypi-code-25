import os

class Assets(object):
    """
    Access test assets in ocrd-assets
    """

    def __init__(self, baseurl=None):
        self.baseurl = baseurl

    def url_of(self, path, baseurl=None):
        """
        Get the URL of an asset
        """
        if baseurl is None:
            baseurl = self.baseurl
        return self.baseurl + path

if 'OCRD_BASEURL' in os.environ:
    assets = Assets(os.environ['OCRD_BASEURL'])
else:
    assets = Assets('file://' + os.path.dirname(os.path.realpath(__file__)) + '/')
