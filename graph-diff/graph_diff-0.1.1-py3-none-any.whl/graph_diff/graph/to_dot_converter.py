import pydot

# exception in rules of importing
from graph_diff.graph_diff_algorithm.graph_map import GraphMap
from .graph_with_repetitive_nodes_with_root import GraphWithRepetitiveNodesWithRoot


class RNRGraphToDotConverter:
    """Class for conversions of graph objects to pydot.Dot"""

    def __init__(self,
                 separator='',
                 graph_type='digraph',
                 node_shape='circle',
                 general_color='black',
                 added_color='green',
                 deleted_color='red'):
        """

        :param separator:       a unique identifier added to all element names
        added to resulting pydot.Dot objects
        :param graph_type:      type of a graph to be printed
        :param node_shape:      shape of the nodes
        :param general_color:   color of not touched elements
        :param added_color:     color of added to the graph elements
        :param deleted_color:   color of deleted from the graph elements
        """

        self._separator = separator
        self._graph_type = graph_type
        self._node_shape = node_shape
        self._general_color = general_color
        self._added_color = added_color
        self._deleted_color = deleted_color

    def __node_to_str_converter(self,
                                node: GraphWithRepetitiveNodesWithRoot.LabeledRepetitiveNode,
                                addition="") -> str:
        """
        Converts graph node to string.
        Is guaranteed to be unique for a unique node.

        :param node:        node to be converted
        :param addition:    additional string identifier if needed
        :return:            string representation of the node
        with contained by the converter separator at the end
        """
        return '_'.join([str(node.Label), str(node.Number), addition, self._separator])

    def convert_graph(self,
                      graph: GraphWithRepetitiveNodesWithRoot) -> pydot.Dot:
        """
        Converts graph to pydot.Dot.

        :param graph:   graph to be converted
        :return:        pydot.Dot object, ready to be printed
        """

        dot = pydot.Dot(graph_type=self._graph_type)

        node_to_dot = {node: pydot.Node(self.__node_to_str_converter(node),
                                        color=self._general_color,
                                        label=str(node.Label),
                                        shape=self._node_shape)
                       for node in graph}

        for _, dot_node in node_to_dot.items():
            dot.add_node(dot_node)

        for from_node in graph:
            for to_node in graph.get_list_of_adjacent_nodes(from_node):
                dot.add_edge(pydot.Edge(node_to_dot[from_node],
                                        node_to_dot[to_node]))

        return dot

    def convert_graph_map(self, graph_map: GraphMap) -> pydot.Dot:
        """
        Converts GraphMap object to pydot.Dot.
        GraphMap is a difference between two graphs,
        so the pydot.Dot result is an illustration of that.

        :param graph_map:   GraphMap object to be converted
        :return:            pydot.Dot ready to be printed
        """

        # For printing all methods of GraphMap have to be used
        # so it is necessary for all the computations to be done
        graph_map.eval_difference_complete()

        dot = pydot.Dot(graph_type='digraph')

        # Parameter addition in __node_to_str_converter method
        # indicates the node's origin. 1 if from the first graph and 2 if from the second
        node_to_dot = {}
        for node in graph_map.get_node_overlap_from_first():
            node_to_dot[node, 1] = pydot.Node(self.__node_to_str_converter(node, '1'),
                                              color=self._general_color,
                                              label=str(node.Label),
                                              shape=self._node_shape)
        for node in graph_map.get_nodes_in_1_not_in_2():
            node_to_dot[node, 1] = pydot.Node(self.__node_to_str_converter(node, '1'),
                                              color=self._deleted_color,
                                              label=str(node.Label),
                                              shape=self._node_shape)
        for node in graph_map.get_nodes_in_2_not_in_1():
            node_to_dot[node, 2] = pydot.Node(self.__node_to_str_converter(node, '2'),
                                              color=self._added_color,
                                              label=str(node.Label),
                                              shape=self._node_shape)

        for _, dot_node in node_to_dot.items():
            dot.add_node(dot_node)

        def try_match_from1(try_node):
            """
            Map node from second graph to first via graph_map from outer scope.
            If there is no match, the parameter is returned.

            :param try_node:    node from second graph to be mapped
            :return:            tuple node from one of the graphs and
            number of the origin graph
            """

            if try_node in graph_map.get_node_overlap_from_second():
                return graph_map.map_from_2(try_node), 1
            return try_node, 2

        for (from_node, to_node) in graph_map.get_edge_overlap_from_first():
            dot.add_edge(pydot.Edge(node_to_dot[from_node, 1],
                                    node_to_dot[to_node, 1],
                                    color=self._general_color))
        for (from_node, to_node) in graph_map.get_edges_in_1_not_in_2():
            dot.add_edge(pydot.Edge(node_to_dot[from_node, 1],
                                    node_to_dot[to_node, 1],
                                    color=self._deleted_color))
        for (from_node, to_node) in graph_map.get_edges_in_2_not_in_1():
            dot.add_edge(pydot.Edge(node_to_dot[try_match_from1(from_node)],
                                    node_to_dot[try_match_from1(to_node)],
                                    color=self._added_color))

        return dot


def write_graph(graph: GraphWithRepetitiveNodesWithRoot,
                path,
                separator=""):
    """
    Prints graph by specified path (absolute or relative).
    Result is a .png file.

    :param graph:       graph to be printed
    :param path:        path for a .png to be saved
    :param separator:   a unique identifier if needed
    (there is no use case why would anybody need that but anyway)
    :return:            None
    """
    write_graph.converter = RNRGraphToDotConverter(separator)
    write_graph.converter.convert_graph(graph).write(path, format="png")


def convert_graph(graph: GraphWithRepetitiveNodesWithRoot,
                  separator="",
                  graph_type='digraph',
                  node_shape='circle',
                  general_color='black',
                  added_color='green',
                  deleted_color='red') -> pydot.Dot:
    """
    Alias for fast conversion of graph.
    For description of the parameters examine RNRGraphToDotConverter.__init__

    :param graph:           graph to be converted to pydot.Dot
    :param separator:
    :param graph_type:
    :param node_shape:
    :param general_color:
    :param added_color:
    :param deleted_color:
    :return:                pydot.Dot representation of graph
    """
    return RNRGraphToDotConverter(separator,
                                  graph_type,
                                  node_shape,
                                  general_color,
                                  added_color,
                                  deleted_color).convert_graph(graph)


def write_diff(graph_map: GraphMap,
               path,
               separator=""):
    """
    Prints graph map by specified path (absolute or relative).
    Result is a .png file.

    :param graph_map:   graph map to be printed
    :param path:        path for a .png to be saved
    :param separator:   a unique identifier if needed
    :return:            None
    """
    write_graph.converter = RNRGraphToDotConverter(separator)
    write_graph.converter.convert_graph_map(graph_map).write(path, format="png")


def convert_diff(graph_map: GraphMap,
                 separator="",
                 graph_type='digraph',
                 node_shape='circle',
                 general_color='black',
                 added_color='green',
                 deleted_color='red') -> pydot.Dot:
    """
    Alias for fast conversion of graph map.
    For description of the parameters examine RNRGraphToDotConverter.__init__

    :param graph_map:       graph map to be converted
    :param separator:
    :param graph_type:
    :param node_shape:
    :param general_color:
    :param added_color:
    :param deleted_color:
    :return:                pydot.Dot representation of graph map
    """
    return RNRGraphToDotConverter(separator,
                                  graph_type,
                                  node_shape,
                                  general_color,
                                  added_color,
                                  deleted_color).convert_graph_map(graph_map)
