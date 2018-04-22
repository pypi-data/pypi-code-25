from minds.utils import requires_auth
from minds.endpoints import *


class InteractAPI:
    @requires_auth
    def delete(self, url: str) -> dict:
        """Delete any sort of post

        :param url: direct url to object to be deleted

        .. note:: requires auth
        """
        return self.con.delete(url).json()

    @requires_auth
    def upvote(self, guid: str) -> dict:
        """Upvote any sort of post

        :param guid: guid of post object

        .. note:: requires auth
        """
        resp = self.con.put(UPVOTE_URLF(guid))
        return resp.json()

    @requires_auth
    def downvote(self, guid) -> dict:
        """Downvote any sort of post

        :param guid: guid of post object

        .. note:: requires auth
        """
        resp = self.con.put(DOWNVOTE_URLF(guid))
        return resp.json()

