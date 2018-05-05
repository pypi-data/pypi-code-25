"""Data structures for "The Simple Tree Lib".
Node and Tree
"""

from collections import deque

class Node(object):
    """Node of a tree.
    Contains references of other nodes
    with witch has output connection.
    Just do A.connections.append(B) for create edge like A->B.
    """

    def __init__(self, name):
        self.name = name
        self.connections = []

    def __str__(self):
        return self.name


class Tree(object):
    """Tree object.
    Contains root node, thats all, wary simple object.
    Can iterete throw nodes, iteration implementation
    allways herarhical sorted!
    """

    def __init__(self, root_node = None ):

        if root_node:
            self.root_node = root_node
        else:
            self.root_node = Node('A')

    def nodes(self):
        """Return herarhical sorted node iterator.
        Stable against circles.
        """

        node_set = set()
        leaves = deque([self.root_node])
        while len(leaves):
            leav = leaves.popleft()
            yield leav
            for cild in leav.connections:
                if cild not in node_set:
                    leaves.append(cild)
                    node_set.add(cild)
