from datetime import datetime
# from typing import Sequence

import sys

if sys.version_info.major == 2:
    try:
        from singledispatch import singledispatch
    except ImportError:
        sys.stderr.write("E:909. singledispatch module missing. Run `pip install singledispatch`")
        sys.exit(1)
else:
    try:
        from functools import singledispatch
    except ImportError:
        sys.stderr.write("E:909. singledispatch module missing. Run `pip install singledispatch`")
        sys.exit(1)


@singledispatch
def serialize(val):
    """Used by default. For base string
    """
    return str(val)


@serialize.register(datetime)
def _datetime(val):
    """
     datetime obj to byte(str) conversion.
    :type val: datetime
    :return String representation of the datetime object
    :rtype :str
    """
    return val.isoformat() + "Z"


@serialize.register(list)
def _list(val):
    """
    list to byte(str) conversion
    :type val:list
    :return String representation of the list object
    :rtype :str
    """
    result = "["
    result += ",".join(serialize(v) for v in val)
    result += "]"
    return result
    pass


@serialize.register(dict)
def _dict(val):
    """
    dict to byte(str) conversion
    :type val:dict
    :return String representation of the dict object
    :rtype :str
    """
    import json
    dump = " ".join(
        k + "=" + json.dumps(v, ensure_ascii=False, default=serialize) for k, v in (val.items()))
    return serialize(dump)


class SerializerClass(object):
    def __init__(self):
        super(SerializerClass, self).__init__()
        self.serialize = singledispatch(self.serialize)
        self.serialize.register(datetime, self._datetime)
        self.serialize.register(list, self._list)
        self.serialize.register(dict, self._dict)

    # @staticmethod
    # def serialize(arg):
    #     return serialize(arg)
    #     pass

    def serialize(self, val):
        """Used by default. For base string
        """
        if isinstance(val, str):
            return val
        else:
            try:
                return val.decode('utf-8')
            except AttributeError:
                return str(val)

    def _unicode(self, val):
        """
        unicode to byte(str) conversion
        :type val: unicode
        :return String representation of the unicode object
        :rtype :str
        """
        return val.encode('utf-8')

    def _datetime(self, val):
        """
         datetime obj to byte(str) conversion.
        :type val: datetime
        :return String representation of the datetime object
        :rtype :str
        """
        return val.isoformat() + "Z"

    def _list(self, val):
        """
        list to byte(str) conversion
        :type val:list
        :return String representation of the list object
        :rtype :str
        """
        result = "["
        result += ",".join(serialize(v) for v in val)
        result += "]"
        return result
        pass

    def _dict(self, val):
        """
        dict to byte(str) conversion
        :type val:dict
        :return String representation of the dict object
        :rtype :str
        """
        import json
        dump = " ".join(
            k + "=" + json.dumps(v, ensure_ascii=False, default=serialize) for k, v in
            (val.items()))
        return serialize(dump)


if __name__ == '__main__':
    test = SerializerClass()
    int_serial = (test.serialize(55555))
    list_serial = (test.serialize([33, 22, 11]))
    dict_serial = (test.serialize({"a": "5678", "b": datetime.now(), "c": list_serial}))
    print("{}:{}\n".format(type(int_serial), int_serial))
    print("{}:{}\n".format(type(list_serial), list_serial))
    print("{}:{}\n".format(type(dict_serial), dict_serial))
