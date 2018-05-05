"""Artists"""

from functools import total_ordering
from homophone.service import UnknownArtistError


@total_ordering
class Artist:
    """An artist"""

    @classmethod
    def from_dict(cls, service, d):
        """Create a new Artist from a dictionary of data"""
        a = cls(service, d["name"])
        a._id = d["id"]
        a._genres = list(d["genres"])
        return a

    def __init__(self, service, artist):
        self._svc = service
        self.name = artist
        self._id = None
        self._genres = None

    @property
    def id(self):
        """Returns a unique ID for the artist"""
        if self._id:
            return self._id
        path = "/search"
        params = {"q": self.name, "type": "artist"}
        resp = self._svc.get(path, params=params)
        try:
            self._id = resp["artists"]["items"][0]["id"]
        except IndexError:
            raise UnknownArtistError(self.name)
        return self._id

    @property
    def genres(self):
        """Returns a list of genres associated with this artist."""
        if self._genres is not None:
            return self._genres
        path = "/artists/" + self.id
        resp = self._svc.get(path)
        self._genres = resp["genres"]
        return self._genres

    def related_artists(self):
        """Returns a list of artists that sound like the given artist."""
        path = "/artists/{}/related-artists".format(self.id)
        resp = self._svc.get(path)
        return list(map(lambda d: self.__class__.from_dict(self._svc, d),
                        resp["artists"]))

    def __eq__(self, other):
        return self.name.lower() == other.name.lower()

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.name.lower() < other.name.lower()

    def __str__(self):
        return "Artist(service={!r}, artist={!r})".format(self._svc, self.name)
