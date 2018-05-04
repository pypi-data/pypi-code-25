
import os
import csv

FILE_DIR = os.path.dirname(__file__)


class ShowDB(object):

    DATABASE_PATH = os.path.abspath(FILE_DIR + '/' + '../data/shows.csv')

    def __init__(self):

        with open(self.DATABASE_PATH, 'r') as fp:
            reader = csv.reader(fp)
            self._shows = [
                line
                for line in reader
                if not line[0].startswith('#')
            ]

        self._names = [show for show, link, status, rating in self._shows]

    @property
    def shows(self):
        return self._shows

    @property
    def names(self):
        return self._names

    @property
    def length(self):
        return len(self._shows)
