from .pluck import pluck


class Pluckable():
    def pluck(self, *handles):
        return pluck(self, *handles)


class PluckableList(list, Pluckable): pass
class PluckableDict(dict, Pluckable): pass
class PluckableSet(set, Pluckable): pass
