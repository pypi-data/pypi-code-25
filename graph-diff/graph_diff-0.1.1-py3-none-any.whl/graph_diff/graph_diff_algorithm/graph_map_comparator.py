from abc import abstractmethod, ABC

from .graph_map import GraphMap


class GraphMapComparator(ABC):
    """Comparator interface for graph map objects"""

    def compare(self,
                graph_map: GraphMap,
                other_graph_map: GraphMap):
        return self.comparable_representation(graph_map) <= self.comparable_representation(other_graph_map)

    @abstractmethod
    def comparable_representation(self, graph_map: GraphMap): pass


class GraphMapComparatorByEdgeNumAndThenNodeNum(GraphMapComparator):
    def comparable_representation(self,
                                  graph_map: GraphMap):
        return graph_map.get_num_edge_overlap(), graph_map.get_num_node_overlap()


class GraphMapComparatorByEdgeNumAndNodeNumSum(GraphMapComparator):
    def comparable_representation(self,
                                  graph_map: GraphMap):
        return graph_map.get_num_node_overlap() + graph_map.get_num_edge_overlap()


class GraphMapComparatorByNodeNumAndThenEdgeNum(GraphMapComparator):
    def comparable_representation(self,
                                  graph_map: GraphMap):
        return graph_map.get_num_node_overlap(), graph_map.get_num_edge_overlap()


class GraphMapComparatorByNodeNum(GraphMapComparator):
    def comparable_representation(self,
                                  graph_map: GraphMap):
        return graph_map.get_num_node_overlap()


class GraphMapComparatorByEdgeNum(GraphMapComparator):
    def comparable_representation(self,
                                  graph_map: GraphMap):
        return graph_map.get_num_edge_overlap()


class GraphMapComparatorNegative(GraphMapComparator):
    def compare(self,
                graph_map: GraphMap,
                other_graph_map: GraphMap):
        return self.comparable_representation(graph_map) > self.comparable_representation(other_graph_map)

    @abstractmethod
    def comparable_representation(self,
                                  graph_map: GraphMap): pass


class GraphMapComparatorByEdgeDiffAndThenNodeDiff(GraphMapComparatorNegative):
    def comparable_representation(self, graph_map: GraphMap):
        graph_map.eval_difference_complete()
        return -(len(graph_map.get_nodes_in_1_not_in_2()) +
                 len(graph_map.get_nodes_in_2_not_in_1()) +
                 len(graph_map.get_edges_in_1_not_in_2()) +
                 len(graph_map.get_edges_in_2_not_in_1()))
