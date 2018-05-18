from renderer.bridge import Renderer, Implementor, singledispatch as sd


class VersionTwoRenderer(Renderer):
    def __init__(self, target='code', imp=None):
        super(VersionTwoRenderer, self).__init__(target=target, imp=imp)

    def _stdout(self, val):
        # type: (str) -> str
        return val
        pass

    def _file(self, val):
        # type: (str) -> str
        return val
        pass

    def _db(self, val):
        # type: (str) -> str
        return val
        pass

    def _code(self, val):
        """

        :type val: any
        :rtype:unicode
        """
        return val.decode(encoding='utf-8', )
        pass


class VersionTwoImplementor(Implementor):
    """
    Implement the Implementor interface and define its concrete
    implementation.
    """

    def __init__(self):
        super(VersionTwoImplementor, self).__init__()

    def serialize(self, data):
        return str(data)
        pass

    def version_specific_registrations(self):
        self.serialize = sd(self.serialize)
        self.serialize.register(unicode, self._unicode)
        pass

    def _unicode(self, val):
        """
        unicode to byte(str) conversion
        :type val: unicode
        :return String representation of the unicode object
        :rtype :str
        """
        return val.encode('utf-8')
