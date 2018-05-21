from nameko.extensions import DependencyProvider
from redis import StrictRedis, Redis


class Redis(DependencyProvider):
    def __init__(self, config_key="REDIS_URI", strict=True, **options):
        self.provider_class = StrictRedis if strict else Redis
        self.config_key = config_key
        self.client = None

    def setup(self):
        self.redis_uri = self.container.config[self.config_key]

    def start(self):
        self.client = self.provider_class.from_url(self.redis_uri, **self.options)

    def stop(self):
        self.client = None

    def kill(self):
        self.client = None

    def get_dependency(self, worker_ctx):
        return self.client
