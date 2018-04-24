from .graph_with_repetitive_nodes_exceptions import GraphWithRepetitiveNodesKeyError
from .graph_with_repetitive_nodes_exceptions import LabeledRepetitiveNodePositiveArgumentException


class GraphWithRepetitiveNodesWithRoot:
    """Graph class with labeled nodes and explicit root."""

    class LabeledRepetitiveNode:
        """Class for labeled node."""

        def __hash__(self) -> int:
            return hash((self.Label, self.Number))

        def __eq__(self,
                   node) -> bool:
            return self.Label == node.Label and self.Number == node.Number

        def __init__(self,
                     label,
                     number: int):
            self.__Label = str(label)
            self.__Number = number

        def __str__(self):
            return 'Node: ({}, {})'.format(self.Label, self.Number)

        def __repr__(self):
            return 'Node: ({}, {})'.format(self.Label, self.Number)

        def __lt__(self,
                   other):
            return self.Label < other.Label if self.Label != other.Label else self.Number < other.Number

        @property
        def Label(self):
            return self.__Label

        @Label.setter
        def Label(self,
                  label: int):
            if label < 0:
                raise LabeledRepetitiveNodePositiveArgumentException("Label should not be negative!")
            self.__Label = label

        @property
        def Number(self):
            return self.__Number

        @Number.setter
        def Number(self,
                   number: int):
            if number < 0:
                raise LabeledRepetitiveNodePositiveArgumentException("Label should not be negative!")
            self.__Number = number

    ROOT = LabeledRepetitiveNode("0", 1)

    def __init__(self):
        # One node is added when created
        self._adjacency_list = {self.ROOT: set()}

    def __contains__(self,
                     item):
        return item in self._adjacency_list.keys()

    def __iter__(self):
        return iter(self._adjacency_list.keys())

    def __len__(self):
        return len(self._adjacency_list)

    def add_node(self,
                 new_node: LabeledRepetitiveNode):
        """
        :param new_node:    node to be added
        :return:            self
        """
        if new_node not in self._adjacency_list.keys():
            self._adjacency_list[self.ROOT].add(new_node)
            self._adjacency_list[new_node] = set()
        return self

    def add_edge(self,
                 from_node: LabeledRepetitiveNode,
                 to_node: LabeledRepetitiveNode):
        """
        Adds edge from from_node to to_node.
        Nodes are added to the graph if needed.
        :param from_node:   starting node
        :param to_node:     ending node
        :return:
        """
        self.add_node(from_node)
        self.add_node(to_node)
        self._adjacency_list[from_node].add(to_node)
        if to_node in self._adjacency_list[self.ROOT] and from_node != self.ROOT:
            self._adjacency_list[self.ROOT].remove(to_node)
        return self

    def add_edge_exp(self,
                     from_node: LabeledRepetitiveNode,
                     to_node: LabeledRepetitiveNode):
        """
        Adds edge from from_node to to_node.
        If nodes are not found in graph, GraphWithRepetitiveNodesKeyError is raised.
        :param from_node:   starting node
        :param to_node:     ending node
        :return:
        """
        if from_node not in self or to_node not in self:
            raise GraphWithRepetitiveNodesKeyError("Adding edge from or to not valid nodes")
        self._adjacency_list[from_node].add(to_node)
        if to_node in self._adjacency_list[self.ROOT] and from_node != self.ROOT:
            self._adjacency_list[self.ROOT].remove(to_node)
        return self

    def get_list_of_adjacent_nodes(self, node) -> [LabeledRepetitiveNode]:
        return self._adjacency_list[node] if node in self else []


def lr_node(label, number: int):
    """
    Alias for GraphWithRepetitiveNodesWithRoot.LabeledRepetitiveNode.__init__
    :param label:
    :param number:
    :return:        a new node
    """
    return GraphWithRepetitiveNodesWithRoot.LabeledRepetitiveNode(label, number)


def rnr_graph():
    """
    Alias for GraphWithRepetitiveNodesWithRoot.__init__
    :return:    a new graph
    """
    return GraphWithRepetitiveNodesWithRoot()
