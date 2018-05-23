"""
-------------------------------------------------
   Author :       galen
   date：          2018/5/21
-------------------------------------------------
   Description:
-------------------------------------------------
"""


class OsmBaseException(Exception):
    def __init__(self, message):
        super(OsmBaseException, self).__init__()
        self._message = message

    def __str__(self):
        return '{0}.'.format(self._message)

    def __repr__(self):
        return self.__str__()

    def __unicode__(self):
        return '{0}.'.format(self._message)

    @property
    def msg(self):
        return self._message


class PagesNotExist(OsmBaseException):
    pass


class InvalidRelationId(OsmBaseException):
    pass


class BoundaryError(OsmBaseException):
    pass
