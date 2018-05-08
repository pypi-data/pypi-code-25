from typing import List

import aiohttp

from .exceptions import InvalidKeyException, PixelException, GuildNotFound, \
    PlayerNotInGuild, PlayerNotFound, NoSessionForPlayer
from .gametypes import GameType
from .models.boosters import Booster
from .models.friends import Friend
from .models.guilds import Guild, GuildBanner, GuildMember, GuildTag
from .models.leaderboards import Leaderboard, LeaderboardMember
from .models.players import Player, PlayerAchievements, \
    PlayerRank, PixelAchievements
from .models import stats
from .models.sessions import PlayerSession
from .utils import clean_uuid, get_player_uuid

BASE_API_URL = "https://api.hypixel.net{}"


class PixelClient:

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._session = aiohttp.ClientSession()
        self._achievements = PixelAchievements()

    async def _request(self, route: str, params: dict=None):
        pass

    async def boosters(self) -> List[Booster]:
        params = {"key": self._api_key}
        async with self._session.get(BASE_API_URL.format("/boosters"), params=params) as r:
            if not r.status == 200:
                raise PixelException(
                    "Error occurred. "
                    "Status code: {0.status}. "
                    "Reason: {0.reason}".format(r)
                )
            data = await r.json()
        if not data["success"]:
            if data["cause"] == "Invalid API key!":
                raise InvalidKeyException(data["cause"])
            else:
                raise PixelException("Error: {}".format(data["cause"]))
        else:
            raw_boosters = data["boosters"]
            boosters = []
            for r_b in raw_boosters:
                boosters.append(Booster(
                    r_b["_id"], r_b["purchaserUuid"], r_b["amount"],
                    r_b["originalLength"], r_b["length"], r_b["gameType"],
                    r_b["dateActivated"], stacked=r_b.get("stacked", None)
                ))
            return boosters

    async def find_guild_by_name(self, name: str) -> str:
        params = {
            "key": self._api_key,
            "byName": name
        }
        async with self._session.get(BASE_API_URL.format("/findGuild"), params=params) as r:
            data = await r.json()
        if data["success"]:
            if data["guild"] is None:
                raise GuildNotFound()
            return data["guild"]

    async def find_guild_by_uuid(self, uuid: str) -> str:
        params = {
            "key": self._api_key,
            "byUuid": clean_uuid(uuid)
        }
        async with self._session.get(BASE_API_URL.format("/findGuild"), params=params) as r:
            data = await r.json()
        if data["success"]:
            if data["guild"] is None:
                raise PlayerNotInGuild()
            return data["guild"]

    async def friends(self, uuid: str) -> List[Friend]:
        params = {
            "key": self._api_key,
            "uuid": clean_uuid(uuid)
        }
        async with self._session.get(BASE_API_URL.format("/friends"), params=params) as r:
            data = await r.json()

        if data["success"]:
            friends_list = []
            for raw_friend in data["records"]:
                friends_list.append(
                    Friend(
                        raw_friend["_id"],
                        raw_friend["uuidSender"],
                        raw_friend["uuidReceiver"],
                        raw_friend["started"]
                    )
                )
            return friends_list

    async def guild(self, guild_id: str) -> Guild:
        params = {
            "key": self._api_key,
            "id": guild_id
        }
        async with self._session.get(BASE_API_URL.format("/guild"), params=params) as r:
            data = await r.json()
        if data["success"]:
            if data["guild"] is None:
                raise GuildNotFound()
            guild = data["guild"]
            members = []
            for m in guild["members"]:
                members.append(GuildMember(m))
 
            tag = GuildTag(guild.get("tag", None), guild.get("tagColor", None))
            guild_can_motd = guild.get("canMotd", False)
            guild_can_party = guild.get("canParty", False)
            guild_can_tag = guild.get("canTag", False)
            guild_joinable = guild.get("joinable", False)
            vip_count = guild.get("vipCount", 0)
            mvp_count = guild.get("mvpCount", 0)
            banner = GuildBanner(
                guild["banner"]["Base"], guild["banner"]["Patterns"]
            )
            return Guild(
                guild["_id"], guild["bankSizeLevel"], guild_can_motd,
                guild_can_party, guild_can_tag, guild["coins"],
                guild["coinsEver"], guild["created"], guild_joinable,
                guild["memberSizeLevel"], members, guild["name"], tag,
                banner, vip_count, mvp_count
            )

    async def leaderboards(self) -> List[Leaderboard]:
        params = {
            "key": self._api_key
        }
        async with self._session.get(BASE_API_URL.format("/leaderboards"), params=params) as r:
            data = await r.json()
        if data["success"]:
            raw_leaderboards = data["leaderboards"]
            leaderboard_list = []
            for game, lbs in raw_leaderboards.items():
                game_type = getattr(GameType, game)
                for lb in lbs:
                    leaders = []
                    for l in lb["leaders"]:
                        leaders.append(LeaderboardMember(l))
                    leaderboard_list.append(
                        Leaderboard(
                            lb["path"], lb["prefix"], lb["count"],
                            leaders, lb["title"], game_type
                        )
                    )
            return leaderboard_list

    async def player_from_name(self, name: str) -> Player:
        uuid = await get_player_uuid(name, self._session)
        if uuid is None:
            raise PlayerNotFound()
        return await self.player_from_uuid(uuid)

    async def player_from_uuid(self, uuid: str) -> Player:
        params = {
            "key": self._api_key,
            "uuid": uuid
        }
        async with self._session.get(BASE_API_URL.format("/player"), params=params) as r:
            data = await r.json()
        if not bool(data["player"]):
            raise PlayerNotFound()
        player_data = data["player"]
        player_rank = PlayerRank.from_player_data(player_data)
        player_achievements = PlayerAchievements(player_data, self._achievements)
        most_recent_game_type = getattr(GameType, player_data["mostRecentGameType"])
        player_stats = []
        for k, v in player_data["stats"].items():
            player_stats.append(getattr(stats, k + "Stats")(v))
        if "housingMeta" in player_data:
            player_stats.append(stats.HousingStats(player_data["housingMeta"]))
        return Player(
            player_data["_id"], player_data["displayname"], player_data["firstLogin"],
            player_data["lastLogin"], player_data["karma"], player_data["networkExp"],
            player_rank, player_data["lastLogout"], player_achievements,
            player_stats, most_recent_game_type
        )
    
    async def session(self, uuid: str) -> PlayerSession:
        params = {
            "key": self._api_key,
            "uuid": uuid
        }
        async with self._session.get(BASE_API_URL.format("/session"), params=params) as r:
            data = await r.json()
        if not data["session"]:
            raise NoSessionForPlayer()
        else:
            return PlayerSession(data["session"])


