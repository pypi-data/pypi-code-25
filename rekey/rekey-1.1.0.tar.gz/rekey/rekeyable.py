from .rekey import rekey


class Rekeyable():
    def rekey(self, key_handle=None, value_handle=None):
        return rekey(self, key_handle, value_handle)


class RekeyableList(list, Rekeyable): pass
class RekeyableDict(dict, Rekeyable): pass
class RekeyableSet(set, Rekeyable): pass
