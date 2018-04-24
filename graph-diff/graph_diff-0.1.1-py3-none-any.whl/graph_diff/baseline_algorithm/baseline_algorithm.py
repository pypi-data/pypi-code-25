from graph_diff.graph import GraphWithRepetitiveNodesWithRoot, lr_node
from graph_diff.graph_diff_algorithm import GraphMap, GraphMapComparator, \
    GraphMapComparatorByEdgeNum, GraphDiffAlgorithm


class BaselineAlgorithm(GraphDiffAlgorithm):
    """
    Baseline graph diff algorithm.
    Main idea - brute-force search.
    Complexity is exponential.
    """

    class BLPermutationsForLabel:
        def __init__(self, label: int, graph):
            self._label = label
            self._length_of_another_graph = len(graph.get(label))

        def list_map_permutations(self,
                                  list_to_perm,
                                  current):
            """
            :param list_to_perm:    list of possible permutations
            :param current:         current match length
            :return:
            """

            if self._length_of_another_graph <= current:
                return [[]]

            res = []
            list_copy = list_to_perm.copy()
            for i in range(0, len(list_to_perm)):
                list_copy[0], list_copy[i] = list_copy[i], list_copy[0]
                res += [[list_copy[0]] + perm
                        for perm in self.list_map_permutations(list_copy[1:], current + 1)]
            if len(list_to_perm) + current < self._length_of_another_graph:
                res += [[lr_node(self._label, 0)] + perm
                        for perm in self.list_map_permutations(list_copy, current + 1)]
            return res

    class RNRGraphForBLAlg:
        def __init__(self, graph: GraphWithRepetitiveNodesWithRoot):
            from collections import defaultdict
            self._label_to_node_map = defaultdict(list)
            self._nodes_in_graph = list(graph)
            for node in graph:
                self._label_to_node_map[node.Label].append(node)

        def get(self, label: int):
            return self._label_to_node_map[label]

        def __iter__(self):
            return iter([label
                         for label, node_list in self._label_to_node_map.items()
                         if bool(node_list)])

        def __len__(self):
            return len(self._label_to_node_map.keys())

        def keys(self):
            return self._nodes_in_graph

        def items(self):
            return self._label_to_node_map.items()

        def extend_graph(self, graph):
            for label in graph:
                if label not in self:
                    self._label_to_node_map[label] = []
            return self

    def __init__(self,
                 comparator: GraphMapComparator = GraphMapComparatorByEdgeNum()):
        """
        :param comparator:  object to compare graph maps and to choose max
        (default is comparison by number of common edges because of theoretical results)
        """
        self.comparator = comparator

    def construct_diff(self,
                       graph1: GraphWithRepetitiveNodesWithRoot,
                       graph2: GraphWithRepetitiveNodesWithRoot) -> GraphMap:

        graph1_internal = BaselineAlgorithm.RNRGraphForBLAlg(graph1)
        graph2_internal = BaselineAlgorithm.RNRGraphForBLAlg(graph2)

        graph1_internal.extend_graph(graph2_internal)
        graph2_internal.extend_graph(graph1_internal)

        def produce_all_possible_maps(graph_maps_for_each_label):
            from functools import reduce
            from itertools import product
            graph_maps_for_each_label = [graph_map
                                         for _, graph_map in graph_maps_for_each_label.items()]
            return reduce(product, graph_maps_for_each_label)

        def sum_tuples(pair):
            if type(pair) == tuple:
                pair, dictionary = pair
                return list(dictionary.items()) + list(sum_tuples(pair))
            elif type(pair) == dict:
                return pair.items()
            raise Exception("Unexpected condition in BaselineAlgorithm.construct_diff.sum_tuples")

        graph_maps = self.graph_maps_for_each_label(graph1_internal, graph2_internal)
        graph_maps = produce_all_possible_maps(graph_maps)
        graph_maps = [dict(sum_tuples(pair)) for pair in graph_maps]
        graph_maps = [GraphMap.construct_graph_map(graph_map, graph1, graph2) for graph_map in graph_maps]

        return max(graph_maps, key=lambda x: self.comparator.comparable_representation(x))

    def graph_maps_for_each_label(self, graph1, graph2):
        """
        Produces all possible permutations within each label.

        :param graph1:  first graph
        :param graph2:  second graph
        :return:        dict of labels to tuples of maps
        """
        permutes_for_label = BaselineAlgorithm.BLPermutationsForLabel
        res = {label: self.zip_all(l1,
                                   permutes_for_label(label, graph1).list_map_permutations(l2, 0))
               for (label, l1), (label2, l2) in zip(sorted(graph1.items()), sorted(graph2.items()))}
        res = {label: ({node_from_self: node_from_graph
                        for node_from_self, node_from_graph in zip(lr1, lr2)
                        if node_from_self.Number != 0 or node_from_graph.Number != 0}
                       for lr1, lr2 in label_permutes)
               for label, label_permutes in res.items()}
        return res

    @staticmethod
    def zip_all(l1, l2_perms):
        return [(l1, l2) for l2 in l2_perms]
