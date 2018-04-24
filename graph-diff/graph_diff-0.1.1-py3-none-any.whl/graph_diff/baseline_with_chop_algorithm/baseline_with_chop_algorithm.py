from graph_diff.baseline_algorithm import BaselineAlgorithm


# TODO: the algorithm
class BaselineWithChopAlgorithm(BaselineAlgorithm):
    class BLPWCPermutations:
        def __init__(self, graph1: BaselineAlgorithm.RNRGraphForBLAlg, graph2: BaselineAlgorithm.RNRGraphForBLAlg):
            self._graph1 = graph1
            self._graph2 = graph2
            self.max_score = (0, 0)
            self.best_map = {}
            self.current_map = {}

        def get_best_graph_map_in_label(self, label, passed_list: int, list_to_perm, current):
            if passed_list >= len(self._graph1.get(label)):
                self.get_next_graph_map(current)
            list_copy = list_to_perm.copy()
            for i in range(0, len(list_to_perm)):
                list_copy[0], list_copy[i] = list_copy[i], list_copy[0]
                self.add_to_current(list_copy[0])
                local_score_plus = self.get_current_local_score_plus(list_copy[0], self._graph2.get(label)[passed_list])
                self.get_best_graph_map_in_label(label, passed_list + 1, list_copy[1:], current + local_score_plus)
                self.remove_from_current(list_copy[0])
            self.get_best_graph_map_in_label(label, passed_list + 1, list_to_perm, current)

        def get_next_graph_map(self, current):
            pass

        def add_to_current(self, param, label, passed_list):
            self.current_map[param] = self._graph2.get(label)[passed_list]

        def get_current_local_score_plus(self, param, mapped_node):
            local_score_plus = (0, int(param.Number != 0))
            # local_score_plus[0] += sum([ int(node in ) for node in ])


        def remove_from_current(self, param, label, passed_list):
            self.current_map.pop(param, None)


    def graph_maps_for_each_label(self, graph1, graph2): pass
