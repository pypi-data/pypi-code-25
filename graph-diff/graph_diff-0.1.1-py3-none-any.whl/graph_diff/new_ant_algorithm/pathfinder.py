import numpy

from graph_diff.graph import GraphWithRepetitiveNodesWithRoot
from graph_diff.new_ant_algorithm import parameters
from graph_diff.new_ant_algorithm.pheromon_table import PheromonTable


class Pathfinder:
    """Class for probabilistic choice of a match of two graphs"""

    ALPHA = parameters.ALPHA
    BETA = parameters.BETA

    def __init__(self,
                 graph1: GraphWithRepetitiveNodesWithRoot,
                 graph2: GraphWithRepetitiveNodesWithRoot,
                 pheromon: PheromonTable):
        """
        :param graph1:      first graph
        :param graph2:      second graph
        :param pheromon:    pheromon table (should not be modified!)
        """

        self.graph1 = graph1
        self.graph2 = graph2
        self.pheromon = pheromon

        # O(V ** 2)
        self.edges1 = {(u, u1)
                       for u in self.graph1
                       for u1 in self.graph1.get_list_of_adjacent_nodes(u)}
        # O(V ** 2)
        self.edges2 = {(v, v1)
                       for v in self.graph2
                       for v1 in self.graph2.get_list_of_adjacent_nodes(v)}

        self.score = 0
        self.path = None

        self.pheromon_factors = None
        self.score_factors = None

    # O(V ** 3)
    def find_path(self):
        """
        Probabilistic choice of graph match.

        :return:    None
        """

        # O(V ** 2)
        select_from_set = {(u, u1)
                           for u in self.graph1
                           for u1 in self.graph2
                           if u.Label == u1.Label}
        selected_dict = {}
        self.score = 0

        self.pheromon_factors = {}
        self.score_factors = {(u, u1): 1
                              for u, u1 in select_from_set}

        # O(V * cycle) - because only V choices
        while len(select_from_set) != 0:
            probabilities = {}

            # O(V ** 2)
            for u, u1 in select_from_set:
                pheromon_factor = self.pheromon_factors[u, u1] \
                    if (u, u1) in self.pheromon_factors.keys() \
                    else 1
                score_factor = self.score_factors[u, u1]

                probability = pheromon_factor ** self.ALPHA * score_factor ** self.BETA
                probabilities[u, u1] = probability

            # O(V ** 2)
            prob_sum = sum(probabilities.values())
            for u, u1 in probabilities.keys():
                probabilities[u, u1] /= prob_sum

            # O(V ** 2)?
            a = list(probabilities.keys())
            chosen = numpy.random.choice(a=len(a),
                                         p=list(probabilities.values()))

            chosen = a[chosen]
            v, v1 = chosen[0], chosen[1]

            self.score += self.score_factors[v, v1]
            selected_dict[v] = v1

            # O(V ** 2)
            for u, u1 in select_from_set:
                if (u, u1) not in self.pheromon_factors.keys():
                    self.pheromon_factors[u, u1] = 0
                self.pheromon_factors[u, u1] += self.pheromon.get_element(u, u1, v, v1)

                if (v, u) in self.edges1 and (v1, u1) in self.edges2:
                    self.score_factors[u, u1] += 1
                if (u, v) in self.edges1 and (u1, v1) in self.edges2:
                    self.score_factors[u, u1] += 1

            # O(V ** 2)?
            set_to_extract = {(v, u) for u in self.graph2} | {(u1, v1) for u1 in self.graph1}
            select_from_set -= set_to_extract

        self.path = selected_dict

        return selected_dict
