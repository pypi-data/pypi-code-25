from minds.utils import requires_auth
from minds.endpoints import *


class NewsfeedAPI:
    def newsfeed_single(self, guid, offset: int=None, limit: int=12) -> dict:
        """Returns single newsfeed post

        :param guid: post guid
        :param offset: pagination offset
        :param limit: pagination limit
        """
        return self._directory(NEWSFEED_SINGLE_URLF(guid), offset, limit)

    @requires_auth
    def newsfeed_subscribed(self, offset: int=None, limit: int=12) -> dict:
        """Returns *newsfeed* section *subscribed* subsection posts

        :param offset: pagination offset
        :param limit: pagination limit

        .. note:: requires auth
        """
        return self._directory(NEWSFEED_URL, offset, limit)

    def newsfeed_top(self, offset: int=None, limit: int=12) -> dict:
        """Returns *newsfeed* section *subscribed* subsection posts

        :param offset: pagination offset
        :param limit: pagination limit
        """
        return self._directory(NEWSFEED_TOP_URL, offset, limit)

    def newsfeed_boost(self, offset: int=None, limit: int=12) -> dict:
        """Returns *newsfeed* section *boost* subsection posts

        :param offset: pagination offset
        :param limit: pagination limit
        """
        return self._directory(NEWSFEED_BOOST_URL, offset, limit)

    def newsfeed_channel(self, channel_guid, offset: int=None, limit: int=12) -> dict:
        """Returns *newsfeed* section *channel* subsection posts

        :param offset: pagination offset
        :param limit: pagination limit
        """
        return self._directory(NEWSFEED_CHANNEL_URLF(channel_guid), offset, limit)
