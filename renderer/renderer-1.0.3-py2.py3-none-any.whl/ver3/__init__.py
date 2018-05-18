from renderer.bridge import Renderer, Implementor, singledispatch


class VersionThreeRenderer(Renderer):
    """ Renderer subclass that defines how python3 formats str for different output destinations
    """

    def __init__(self, target='code', imp=None):
        super(VersionThreeRenderer, self).__init__(target=target, imp=imp)

    def to_bytes(self, val):
        # type: (str) -> bytes
        return bytes(val, encoding='utf-8')

    def _stdout(self, val):
        # type: (str) -> str
        return val
        pass

    def _file(self, val):
        # type: (str) ->bytes
        return self.to_bytes(val)
        pass

    def _db(self, val):
        # type: (str) -> bytes
        return self.to_bytes(val)
        pass

    def _code(self, val):
        # type: (str) -> str
        return val
        pass


class VersionThreeImplementor(Implementor):
    """
    Implement the Implementor interface and define its concrete
    implementation.
    """

    def __init__(self):
        super(VersionThreeImplementor, self).__init__()

        pass

    def serialize(self, data):
        return data
        pass

    def version_specific_registrations(self):
        self.serialize = singledispatch(self.serialize)
        self.serialize.register(bytes, self._bytes)

    def _bytes(self, val):
        """
        unicode to byte(str) conversion
        :type val: bytes
        :return String representation of the unicode object
        :rtype :str
        """
        # print(val)
        return val.decode('utf-8')
