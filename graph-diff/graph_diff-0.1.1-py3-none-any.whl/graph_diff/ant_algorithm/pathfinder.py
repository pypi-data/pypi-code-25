import logging
from collections import defaultdict

import numpy

from graph_diff.ant_algorithm import parameters
from graph_diff.ant_algorithm.ant_graph import AntGraph


class Pathfinder:
    """Class for probabilistic choice of a match of two graphs"""

    ALPHA = parameters.ALPHA
    BETA = parameters.BETA

    def __init__(self,
                 graph1: AntGraph,
                 graph2: AntGraph,
                 pheromon: [dict],
                 matched: dict):
        """
        :param graph1:      first graph
        :param graph2:      second graph
        :param pheromon:    pheromon table (should not be modified!)
        :param matched:     nodes that are matched anyway
        """

        self.graph1 = graph1
        self.graph2 = graph2
        self.route = None
        self.number_of_nodes_in_first_graph = None
        self.inverse_route = None
        self.initial_score = 0
        self.score = None
        self.scores = {}
        self.chosen_zeroes_label = None
        self.route_set = None

        self.initial_route = [None] * self.graph1.len
        self.initial_route_set = set()
        self.initial_inverse_route = {}
        for node1, node2 in matched.items():
            if node2 is not None:
                self.initial_score += 1
                self.update(graph1.node_indices[node1],
                            graph2.node_indices[node2])

            if node2 is not None:
                self.initial_route[graph1.node_indices[node1]] = graph2.node_indices[node2]
                self.initial_route_set.add(graph1.node_indices[node2])
                self.initial_inverse_route[graph2.node_indices[node2]] = graph1.node_indices[node1]
            else:
                self.initial_route[graph1.node_indices[node1]] = 0

        self.initial_scores = self.scores.copy()
        self.pheromon = pheromon

    def copy_initials(self):
        """
        Restores initial values where needed for a new iteration of the algorithm.
        Linear complexity of size of the answer.

        :return:    self
        """
        self.route = self.initial_route.copy()
        self.inverse_route = self.initial_inverse_route.copy()
        self.route_set = self.initial_route_set.copy()
        self.score = self.initial_score
        self.scores = self.initial_scores.copy()

        return self

    def choose(self,
               u_score: dict,
               v):
        """
        Probabilistic choice of a match for a given node.
        Label size complexity.

        :param u_score: scores addition if v is matched with vertex u
        :param v:       node to be found match with
        :return:        chosen match node
        """

        discussed_label = self.graph1.get_label(v)
        number_of_zeroes = max(0,
                               self.graph1.label_size(discussed_label)
                               - self.graph2.label_size(discussed_label)
                               - self.chosen_zeroes_label[discussed_label])

        probability = [(self.pheromon[v][u] ** self.ALPHA) * (us ** self.BETA)
                       if u not in self.route_set else 0
                       for u, us in u_score.items()]
        values = list(u_score.keys())

        if number_of_zeroes > 0:
            values.append(0)
            probability.append(self.pheromon[v][0] ** self.ALPHA)

        values = [v
                  for i, v in enumerate(values)
                  if probability[i] != 0]
        probability = [p
                       for p in probability
                       if p != 0]

        prob_sum = sum(probability)
        probability = [p / prob_sum
                       for p in probability]

        if not prob_sum:
            chosen = 0
        else:
            chosen = numpy.random.choice(a=values, p=probability)

        return chosen

    def find_route(self):
        """
        Probabilistic choice of graph match.

        :return:    None
        """

        logging.debug('Finding new route')
        self.copy_initials()

        self.chosen_zeroes_label = defaultdict(int)

        # O(V_1 * inner)
        for v in self.graph1:
            assert self.route[v] is None

            # O(label_size_2(v)) = O(V_2)
            u_score = self.find_pair(v)

            # O(label_size_2(v)) = O(V_2)
            chosen = self.choose(u_score, v)
            discussed_label = self.graph1.get_label(v)

            self.route[v] = chosen
            self.inverse_route[chosen] = v

            # O(inc(v) * inc(chosen) + out(v) * out(chosen))
            self.update(v, chosen)

            if chosen == 0:
                self.chosen_zeroes_label[discussed_label] += 1
            else:
                self.route_set.add(chosen)
                self.score += u_score[chosen]
        # Total complexity is O(E_1 * V_2)

        logging.debug('route is {}'.format(self.route))
        self.route = self.route[1:]

    def find_pair(self, v):
        """
        :param v:   node v
        :return:    scores addition if v is matched with vertex u
        """

        u_score = {}
        for u in self.graph2.label(self.graph1.get_label(v)):
            if (v, u) not in self.scores.keys():
                self.scores[v, u] = 1
            u_score[u] = self.scores[v, u]
        return u_score

    def update(self, v, u):
        """
        Update after match v, u has been made.
        Complexity = O(inc(v)*inc(u) + out(v)*out(u)) = O(V_1 * V_2).

        :param v:   node of first graph
        :param u:   node of second graph
        :return:    None
        """
        if v == 0 or u == 0:
            return
        for u1 in self.graph1.outcoming(v):
            for u2 in self.graph2.outcoming(u):
                if (u1, u2) not in self.scores.keys():
                    self.scores[u1, u2] = 1
                self.scores[u1, u2] += 1
        for u1 in self.graph1.incoming(v):
            for u2 in self.graph2.incoming(u):
                if (u1, u2) not in self.scores.keys():
                    self.scores[u1, u2] = 1
                self.scores[u1, u2] += 1
