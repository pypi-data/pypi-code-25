from .dli_request_factory_factory import DliRequestFactoryFactory
from pypermedia import HypermediaClient


class Context(object):
    def __init__(self, api_key, api_root, auth_key):
        self.api_key = api_key
        self.api_root = api_root
        self.auth_key = auth_key
        self.request_factory = DliRequestFactoryFactory(
            api_root, lambda: self.get_header_with_auth()
        ).request_factory
        self.s3_keys = {}

    def get_header_with_auth(self):
        auth_header = "Bearer {}".format(self.auth_key)
        return {"Authorization": auth_header}

    def uri_with_root(self, relative_path):
        return "{}/{}".format(self.api_root, relative_path)

    def get_root_siren(self):
        return HypermediaClient.connect(
            self.api_root, request_factory=self.request_factory
        )
