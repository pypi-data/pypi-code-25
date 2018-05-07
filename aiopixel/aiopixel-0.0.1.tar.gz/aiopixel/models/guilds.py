from datetime import datetime
from typing import List

from ..utils import get_player_name

__all__ = ["Guild", "GuildBanner", "GuildMember", "GuildTag"]


class GuildBanner:
    def __init__(self, base, patterns):
        self.base = base
        self.patterns = []
        for pattern in patterns:
            self.patterns.append(
                BannerPattern(
                    pattern["Pattern"], pattern["Color"]
                )
            )


class BannerPattern:
    def __init__(self, pattern, color):
        self.pattern = pattern
        self.color = color


class GuildMember:

    def __init__(self, member: dict):
        self.uuid = member["uuid"]
        self.rank = member["rank"]
        self.joined = datetime.utcfromtimestamp(member["joined"]/1000)

    async def name(self):
        return await get_player_name(self.uuid)


class GuildTag:

    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color


class Guild:

    def __init__(self, _id: str, bank_size_level: int, can_motd: bool,
                 can_party: bool, can_tag: bool, coins: int, coins_ever: int,
                 created: int, joinable: bool, member_size_level: int,
                 members: List[GuildMember], name: str, tag: GuildTag,
                 banner: GuildBanner, vip_count: int, mvp_count: int):
        self._id = _id
        self.bank_size_level = bank_size_level
        self.can_motd = can_motd
        self.can_party = can_party
        self.can_tag = can_tag
        self.coins = coins
        self.coins_ever = coins_ever
        self.created = datetime.utcfromtimestamp(created/1000)
        self.joinable = joinable
        self.member_size_level = member_size_level
        self.members = members
        self.name = name
        self.tag = tag
        self.banner = banner
        self.vip_count = vip_count
        self.mvp_count = mvp_count
