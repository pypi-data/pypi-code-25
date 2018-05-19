class Node:
    """ Terms Tree Node"""

    def __init__(self, term, data=None):
        """
        :param str term:
        :param dict data: key value pairs
        :param Node parent: parent node
        """
        self.term = term
        self.data = data
        self.parent = None
        self.children = []

    # pickling problem, but tree circular refs is ok in CPython, gc detects that cases
    # @property
    # def parent(self):
    #     return self._parent if self._parent is None else self._parent()
    #
    # @parent.setter
    # def parent(self, node):
    #     self._parent = weakref.ref(node)

    def get_child(self, path):
        if isinstance(path, int):
            path = (path,)
        child = self
        for idx in path:
            child = child.children[idx]
        return child

    def __getitem__(self, item):
        return self.get_child(item)

    def add_child(self, node):
        self.children.append(node)
        node.parent = self

    def add_children(self, nodes):
        self.children.extend(nodes)
        for node in nodes:
            node.parent = self

    def remove_child(self, node):
        self.children.remove(node)
        node.parent = None
        return node

    def __repr__(self):
        if self.data:
            return '%s(%r, %r)' % (self.__class__.__name__, self.term, self.data)
        else:
            return '%s(%r)' % (self.__class__.__name__, self.term)
