import typing

from lxml import etree

from dewi.config.node import Node, NodeList

XmlEmenent = etree._Element


class XPathError(Exception):
    def __init__(self, message: str, xpath_query: str):
        self.query = xpath_query

        super().__init__(f"{message}; query={self.query!r}")


class InvalidXPath(XPathError):
    def __init__(self, xpath_query: str, error: etree.XPathSyntaxError):
        self.error = error

        super().__init__(f"Invalid XPath query, {self.error!r}", xpath_query)


class AmbiguousXPathResults(XPathError):
    def __init__(self, xpath_query: str):
        super().__init__("XPath query has ambiguous results", xpath_query)


class NoXPathResult(XPathError):
    def __init__(self, xpath_query: str):
        super().__init__("XPath query has no result", xpath_query)


class XPath:
    def __init__(self, query: str):
        self._query = query

        try:
            self._xpath = etree.XPath(self._query)

        except etree.XPathSyntaxError as error:
            raise InvalidXPath(query, error)

    def fetch_one(self, dom_node, *, ignore_rest: bool = False):
        result = self._xpath(dom_node)

        if not isinstance(result, list):
            return result

        if len(result) == 0:
            raise NoXPathResult(self._query)
        elif len(result) > 1 and not ignore_rest:
            raise AmbiguousXPathResults(self._query)

        return result[0]

    def fetch_first(self, dom_element):
        return self.fetch_one(dom_element, ignore_rest=True)

    def fetch_all(self, dom_node) -> typing.Iterable:
        return tuple(enumerate(self._xpath(dom_node)))


class Reader:
    """
    Reads data from specified dom_node and returns the read data in read().
    It always creates new object as return value.
    """

    def read(self, dom_node):
        raise NotImplementedError()


class Loader:
    """
    Loads data into the specified node or its child element, and does not return anything.
    Actual implementations uses readers.
    """

    def load(self, dom_node, node: Node):
        raise NotImplementedError()


class XPathReader(Reader):
    def __init__(self, xpath_query: str, value_map: typing.Union[typing.Mapping, None] = None):
        self._xpath = XPath(xpath_query)
        self._value_map = dict(value_map) if value_map else dict()

    def read(self, dom_node):
        result = self._xpath.fetch_one(dom_node)

        if isinstance(result, str):
            result = str(result)

        if result in self._value_map:
            result = self._value_map[result]

        return result


class NodeReader(Reader):
    def __init__(self, node_class: typing.Type[Node], loader: Loader):
        self._node_class = node_class
        self._loader = loader

    def read(self, dom_node) -> Node:
        node = self._node_class()
        self._loader.load(dom_node, node)
        return node


class CompositeLoader(Loader):
    def __init__(self, loaders: typing.List[Loader]):
        self._loaders = list(loaders)

    def load(self, dom_node, node: Node):
        for loader in self._loaders:
            loader.load(dom_node, node)


class MemberLoader(Loader):
    def __init__(self, member: str, reader: Reader):
        self._member = member
        self._reader = reader

    def load(self, dom_node, node: Node):
        node[self._member] = self._reader.read(dom_node)


class XPathReader2(Reader):
    def __init__(self, xpath: str, reader: Reader, ignore_rest: bool = False):
        self._xpath = XPath(xpath)
        self._reader = reader
        self._ignore_rest = ignore_rest

    def read(self, dom_node):
        return self._reader.read(self._xpath.fetch_one(dom_node, ignore_rest=self._ignore_rest))


class NodeListReader(Reader):
    def __init__(self, item_xpath: str, list_item_type: typing.Type[Node], list_item_reader: NodeReader):
        self._item_xpath = XPath(item_xpath)
        self._list_item_type = list_item_type
        self._list_item_reader: NodeReader = list_item_reader

    def read(self, dom_node) -> NodeList:
        result = NodeList(self._list_item_type)

        for x, child_element in self._item_xpath.fetch_all(dom_node):
            result.append(self._list_item_reader.read(child_element))

        return result


class TypeReader(Reader):
    def __init__(self, type_: typing.Type, reader: Reader):
        self._type = type_
        self._reader = reader

    def read(self, dom_node):
        return self._type(self._reader.read(dom_node))


class IntReader(TypeReader):
    def __init__(self, reader: Reader):
        super().__init__(int, reader)


class YesNoToBoolXPathReader(XPathReader):
    """
    Maps "yes" to True, others to False. It can have custom value mapping that maps values only to "yes",
    and "no" can be missing from the mapping as non-"yes" is handled as "no".
    """

    def read(self, dom_node):
        return super().read(dom_node) == "yes"


def main():
    class Archive(Node):
        def __init__(self):
            self.name: str = None
            self.id = ''
            self.days = 0

    class Archives(Node):
        def __init__(self):
            self.archives = NodeList(Archive)

    r1 = NodeReader(
        Archive,
        CompositeLoader([
            MemberLoader('name', XPathReader('@name')),
            MemberLoader('id', XPathReader('@id')),
            MemberLoader('days', TypeReader(int, XPathReader('archive_days/text()')))
        ])

    )

    reader = NodeReader(
        Archives,
        MemberLoader('archives', NodeListReader('archive', Archive, r1))
    )

    with open('/Users/panther/Issues/11813/debug_info-swrzrhbal01-201802201357/config.xml') as f:
        tree = etree.parse(f)

    xpath = XPath('//archive')
    print(r1.read(xpath.fetch_first(tree)))

    print(XPathReader2('//archive', r1, ignore_rest=True).read(tree))

    print(XPathReader2('//archives', reader).read(tree))

    # import inspect
    # print([x[1] for x in inspect.getmembers(Archive()) if x[0][0] != '_'])


"""
    c = Connection(HostTestSupportBalabit())

    class User(Node):
        def __init__(self):
            self.id : int = 0
            self.first_name = ''
            self.last_name = ''
            self.staffgroupid = 0

    UR = NodeReader(
        User,
        CompositeLoader([
            MemberLoader('id', IntReader(XPathReader('id/text()'))),

            MemberLoader('first_name', XPathReader('firstname/text()')),
            MemberLoader('last_name', XPathReader('lastname/text()')),

            MemberLoader('staffgroupid', TypeReader(int, XPathReader('staffgroupid/text()')))
        ])

    )
    x = c.fetch('/Base/Staff/70')
    print(x)
    user: User = UR.read(XPath('/staffusers/staff').fetch_one(etree.fromstring(x)))

    print(user)
    c.put('/Base/Staff/70', dict(firstname=user.first_name, lastname=user.last_name, staffgroupid=7))


    print(c.fetch('/Base/Staff/70'))
"""

if __name__ == main():
    main()
