import asyncio
from collections import namedtuple
class PubgPlayer(): # 플레이어 클래스
    def __init__(self,playername,authinfo):
        self.playername = playername
        self.jsonfile = authinfo.request_get("player", self.playername)
        self.last_matches_id = []
    def get_latest_matches(self):
        if self.jsonfile != None:
            for match_data in self.jsonfile["data"][0]["relationships"]["matches"]["data"]:
                self.last_matches_id.append(match_data['id'])
            return self.last_matches_id
        else:
            return None
    def test(self):
        pass


class PubgMatch(): # 매치 클래스
    def __init__(self,match_ids,playername,authinfo):
        self.jsonfiles = {}
        self.playername = playername
        if match_ids != None :
            self.match_ids = match_ids[0:5]
            tasks = [authinfo.request_get_async('match', game, self.jsonfiles) for game in self.match_ids]
            #loop = asyncio.get_event_loop()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(asyncio.wait(tasks))
        else:
            self.match_ids = None
            self.jsonfiles = None
        self.match_type = []
        self.match_duration = []
        self.winplace = []
        self.damagedealt = []
        self.kills = []
        self.match_dataset = []
        self.match_infoset = []

    def get_data(self):
        if self.jsonfiles != None:
            for match_id in self.match_ids:
                self.match_info = namedtuple('match_info'," ".join(self.jsonfiles[match_id]["data"]["attributes"].keys()))
                self.match_infoset.append(self.match_info(**self.jsonfiles[match_id]["data"]["attributes"]))
                for part in self.jsonfiles[match_id]["included"]:
                    if isinstance(part, dict):
                        if part["type"] == "participant":
                            if part["attributes"]["stats"]["name"] == self.playername:
                                self.match_data = namedtuple('match_data', " ".join(part["attributes"]["stats"].keys()))
                                self.match_dataset.append(self.match_data(**part["attributes"]["stats"]))
            return self.match_dataset, self.match_infoset
        else:
            return None
