import aioredis


class CacheStorage:

    def __init__(self, config, loop):
        self.config = config["redis"]["debug"] if config["debug"] else config["redis"]["production"]
        loop.create_task(self.init_connection())

    async def init_connection(self):
        self.host = self.config["host"]
        self.port = self.config["port"]
        self.password = self.config["password"]
        self.redis_con = await aioredis.create_redis(address=(self.host, self.port), password=self.password)

    async def set(self, key, value):
        await self.redis_con.set(key, value)

    async def set_ex(self, key, value, time_in_sec):
        await self.redis_con.setex(key, time_in_sec, value)

    async def mget(self, *keys):
        return await self.redis_con.mget(*keys)

    async def mset(self, *pairs):
        """pairs key, value"""
        await self.redis_con.mset(*pairs)

    async def get(self, key):
        return await self.redis_con.get(key)

    async def increment(self, key, amount=1):
        await self.redis_con.incrby(key, amount)


# IT'S ONLY FOR METHODS TESTING
if __name__ == "__main__":
    import asyncio
    config = {
        "debug": True,
        "redis": {
            "debug": {
                "port": 6379,
                "host": "localhost",
                "password": None
            }
        }
    }
    loop = asyncio.get_event_loop()

    def main():
        r = CacheStorage(config, loop)
        loop.create_task(_main(r))
        # print(r.redis_con)
        # await r.set("sec", "11101234123")
        # print(r.get("sec"))
    # loop.create_task(main)

    async def _main(conn):
        a = ["qqq", "111", "qqq", "222", "qqq", "333"]
        await asyncio.sleep(1)
        # print(conn.redis_con)
        print(await conn.mget(*a))
        # print(await conn.get("sec"))


    main()
    loop.run_forever()
    # loop.run_until_complete(main())
