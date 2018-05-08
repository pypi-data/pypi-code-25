import aioredis

from oshino import Agent
from functools import partial


class RedisAgent(Agent):

    @property
    def selected_metrics(self):
        return self._data.get("selected", None)

    @property
    def host(self):
        return self._data.get("host", "localhost")

    @property
    def port(self):
        return self._data.get("port", 6379)

    @property
    def password(self):
        return self._data.get("password", None)

    async def create_connection(self):
        return await aioredis.create_redis((self.host, self.port))

    def handle_dict(self, d, prefix):
        for key, stat in d.items():
            service = "{prefix}.{key}".format(prefix=prefix,
                                              key=key)
            if not isinstance(stat, dict):
                yield key, service, stat
            else:
                yield from self.handle_dict(stat, service)

    async def process(self, event_fn):
        logger = self.get_logger()
        redis = await self.create_connection()
        if self.password is not None:
            await redis.auth(self.password)
        info = await redis.info()
        data = dict(map(lambda x: (x[0], (x[1], x[2])),
                    self.handle_dict(info, "redis")))

        hits = int(data["keyspace_hits"][1])
        misses = int(data["keyspace_misses"][1])
        hit_rate = (hits / (hits + misses)) if hits > 0 else 0
        data["hit_rate"] = ("redis.computed.hit_rate", hit_rate)

        for key, (service, stat) in data.items():

            if self.selected_metrics:
                if key not in self.selected_metrics:
                    pass

            metric = partial(event_fn,
                             host=self.host,
                             service=service)
            try:
                metric(metric_f=float(stat))
            except ValueError:  # We've got string metric
                metric(state=stat)

        redis.close()
