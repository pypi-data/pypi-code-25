
from .database import ShowDB


class EZTVManager(object):

    def __init__(self):
        self._db = ShowDB()

    @property
    def db(self):
        return self._db

    @property
    def count(self):
        return self._db.length

    @property
    def names(self):
        return self._db.names

    def filter_by_status(self, status=None):
        if status is None:
            shows = self._db.shows
        else:
            shows = [
                show
                for show in self._db.shows
                if status in show[2]
            ]

        return shows

    def find_show(self, name):
        for show in self._db.shows:
            if name == show[1]:
                return show
