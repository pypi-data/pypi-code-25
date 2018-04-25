# auth setting file
import requests
import aiohttp

urls = {
    "player" : "https://api.playbattlegrounds.com/shards/{0}/players?page[limit]=10&filter[playerNames]=",
    "match" : "https://api.playbattlegrounds.com/shards/pc-kakao/matches/",
}

class PubgAuth:
    def __init__(self, apikey, region='pc-kakao'):
        self.apikey = apikey
        self.region = region
        self.header = {
            "Authorization": self.apikey,
            "Accept": "application/vnd.api+json",
        }
    def request_get(self, type, target):
        endurl = urls[type].format(self.region)+target
        r = requests.get(endurl, headers=self.header)
        if r.status_code == 200:
            my_json = r.json()
        else:
            print("Error : status code:",r.status_code)
            return None
        return my_json

    async def request_get_async(self, type, target, file):
        endurl = urls[type].format(self.region) + target
        async with aiohttp.ClientSession() as session:
            async with session.get(endurl, headers=self.header) as response:
                r = await response.json(content_type=None)
                file[target] = r


