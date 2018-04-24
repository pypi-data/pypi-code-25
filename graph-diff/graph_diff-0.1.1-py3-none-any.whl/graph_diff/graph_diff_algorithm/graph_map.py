from graph_diff.graph import GraphWithRepetitiveNodesWithRoot, lr_node
from .graph_map_exceptions import *


class GraphMap:
    """Class for matching graph objects"""

    def __init__(self):
        self._graph1 = None
        self._graph2 = None
        self._graph_map_1_to_2 = None
        self._graph_map_2_to_1 = None
        self._nodes_in_1_not_in_2 = None
        self._nodes_in_2_not_in_1 = None
        self._edges_in_1_not_in_2 = None
        self._edges_in_2_not_in_1 = None
        self._complete_analysis_done = False

        self._node_overlap_from_second = None
        self._edge_overlap_from_second = None

    @staticmethod
    def construct_graph_map(graph_map_1_to_2,
                            graph1: GraphWithRepetitiveNodesWithRoot,
                            graph2: GraphWithRepetitiveNodesWithRoot):
        """
        Constructs GraphMap object from dict of nodes: nodes and two graphs.
        Only basic computations are made.

        :param graph_map_1_to_2:    dict from nodes of first graph
        to nodes of second graph
        :param graph1:              first graph
        :param graph2:              second graph
        :return:                    GraphMap object
        """

        error_list = []
        for node1, node2 in graph_map_1_to_2.items():
            if node1 not in graph1 and node1.Number != 0:
                error_list.append((node1, 1))
            if node2 not in graph2 and node2.Number != 0:
                error_list.append((node2, 2))

        if len(error_list) > 0:
            raise GraphDoesNotContainMappedNodeException(error_list)

        graph_map = GraphMap()

        graph_map._graph_map_1_to_2 = dict(graph_map_1_to_2)
        graph_map._graph_map_2_to_1 = {node2: node1
                                       for node1, node2 in graph_map._graph_map_1_to_2.items()}

        graph_map._graph1 = graph1
        graph_map._graph2 = graph2
        return graph_map.__eval_difference()

    def map_from_1(self, node):
        """
        Returns match of a node in the second graph.
        If not found, node with number 0 is returned.

        :param node:    node from first graph
        :return:        node from second graph
        """
        if node in self._graph_map_1_to_2.keys():
            return self._graph_map_1_to_2[node]
        return lr_node(node.Label, 0)

    def map_from_2(self, node):
        """
        Returns match of a node in the first graph.
        If not found, node with number 0 is returned.

        :param node:    node from second graph
        :return:        node from first graph
        """
        if node in self._graph_map_2_to_1.keys():
            return self._graph_map_2_to_1[node]
        return lr_node(node.Label, 0)

    def __eval_difference(self):
        """
        Evaluate basic properties.
        Basic fields are considered overlap properties.

        :return:    self
        """

        def nodes_overlap(graph1, graph2):
            return [node_1 for node_1 in graph1 if self.map_from_1(node_1) in graph2]

        def edges_overlap(graph1, graph2):
            return [(from_node_1, to_node_1)
                    for from_node_1 in graph1
                    for to_node_1 in graph1.get_list_of_adjacent_nodes(from_node_1)
                    if self.map_from_1(to_node_1)
                    in graph2.get_list_of_adjacent_nodes(self.map_from_1(from_node_1))]

        self._node_overlap_from_first = nodes_overlap(self._graph1, self._graph2)
        self._num_node_overlap = len(self._node_overlap_from_first)
        self._edge_overlap_from_first = edges_overlap(self._graph1, self._graph2)
        self._num_edge_overlap = len(self._edge_overlap_from_first)

        return self

    def eval_difference_complete(self):
        """
        Evaluate all possible properties.
        Is lazy and evaluated only once.

        :return:    self
        """

        def complement_of_nodes(graph: GraphWithRepetitiveNodesWithRoot, nodes):
            return [node for node in graph if node not in nodes]

        def complement_of_edges(graph: GraphWithRepetitiveNodesWithRoot, edges):
            return [(from_node, to_node)
                    for from_node in graph
                    for to_node in graph.get_list_of_adjacent_nodes(from_node)
                    if (from_node, to_node) not in edges]

        if self._complete_analysis_done:
            return self

        self._node_overlap_from_second = [self.map_from_1(node)
                                          for node in self._node_overlap_from_first]
        self._edge_overlap_from_second = [(self.map_from_1(from_node), self.map_from_1(to_node))
                                          for from_node, to_node in self._edge_overlap_from_first]

        self._nodes_in_1_not_in_2 = complement_of_nodes(self._graph1,
                                                        self._node_overlap_from_first)
        self._nodes_in_2_not_in_1 = complement_of_nodes(self._graph2,
                                                        self._node_overlap_from_second)

        self._edges_in_1_not_in_2 = complement_of_edges(self._graph1,
                                                        self._edge_overlap_from_first)
        self._edges_in_2_not_in_1 = complement_of_edges(self._graph2,
                                                        self._edge_overlap_from_second)

        self._complete_analysis_done = True
        return self

    def get_node_overlap_from_first(self):
        """
        :return:    nodes from first graph that have match in the second graph
        """
        return self._node_overlap_from_first

    def get_edge_overlap_from_first(self):
        """
        :return:    edges from first graph that have match in the second graph
        """
        return self._edge_overlap_from_first

    def get_node_overlap_from_second(self):
        """
        :return:    nodes from second graph that have match in the first graph
        """
        return self._node_overlap_from_second

    def get_edge_overlap_from_second(self):
        """
        :return:    edges from second graph that have match in the first graph
        """
        return self._edge_overlap_from_second

    def get_num_node_overlap(self):
        """
        :return:    number of nodes that have match
        """
        return self._num_node_overlap

    def get_num_edge_overlap(self):
        """
        :return:    number of edges that have match
        """
        return self._num_edge_overlap

    def get_nodes_in_1_not_in_2(self):
        """
        :return:    nodes from first graph that have not match in the second graph
        """
        return self._nodes_in_1_not_in_2

    def get_nodes_in_2_not_in_1(self):
        """
        :return:    nodes from second graph that have not match in the first graph
        """
        return self._nodes_in_2_not_in_1

    def get_edges_in_1_not_in_2(self):
        """
        :return:    edges from first graph that have not match in the second graph
        """
        return self._edges_in_1_not_in_2

    def get_edges_in_2_not_in_1(self):
        """
        :return:    edges from second graph that have not match in the first graph
        """
        return self._edges_in_2_not_in_1

    def get_first_graph(self):
        """
        :return:    first graph
        """
        return self._graph1

    def get_second_graph(self):
        """
        :return:    second graph
        """
        return self._graph2
