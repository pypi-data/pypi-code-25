from graph_diff.graph import GraphWithRepetitiveNodesWithRoot
from graph_diff.graph_diff_algorithm import GraphDiffAlgorithm, GraphMap
from graph_diff.new_ant_algorithm import parameters
from graph_diff.new_ant_algorithm.pathfinder import Pathfinder
from graph_diff.new_ant_algorithm.pheromon_table import PheromonTable


class Algorithm(GraphDiffAlgorithm):
    """
    Realization of heuristic ant algorithm for graph difference problem.
    It is not an exact algorithm, so the mistakes may be made.
    TODO: add accuracy evaluation.
    TODO: add complexity
    TODO: add references.
    """

    P = parameters.P
    NUMBER_OF_ITERATIONS = parameters.NUMBER_OF_ITERATIONS
    NUMBER_OF_AGENTS = parameters.NUMBER_OF_AGENTS
    MAX_NUMBER_OF_ITERATIONS_WITH_THE_SAME_SCORE = parameters.MAX_NUMBER_OF_ITERATIONS_WITH_THE_SAME_SCORE

    def __init__(self):
        self.best_choice = None
        self.best_score = -1

    def construct_diff(self,
                       graph1: GraphWithRepetitiveNodesWithRoot,
                       graph2: GraphWithRepetitiveNodesWithRoot) -> GraphMap:

        self.best_choice = None
        self.best_score = -1

        self.graph1 = graph1
        self.graph2 = graph2

        self.pheromon_table = PheromonTable()

        # O(NoA)
        pathfinders = [Pathfinder(self.graph1, self.graph2, self.pheromon_table) for _ in
                       range(0, self.NUMBER_OF_AGENTS)]

        assert self.NUMBER_OF_ITERATIONS > 0
        assert self.NUMBER_OF_AGENTS > 0

        route = []

        number_of_iterations_with_the_same_score = 0

        # O(NoI * cycle)
        for _ in range(0, self.NUMBER_OF_ITERATIONS):
            number_of_iterations_with_the_same_score += 1

            # O(NoA * cycle)
            for i in range(0, self.NUMBER_OF_AGENTS):
                # O(V ** 3)
                pathfinders[i].find_path()
                if pathfinders[i].score > self.best_score:
                    self.best_choice = pathfinders[i].path
                    self.best_score = pathfinders[i].score
                    number_of_iterations_with_the_same_score = 0

            if self.MAX_NUMBER_OF_ITERATIONS_WITH_THE_SAME_SCORE <= number_of_iterations_with_the_same_score:
                break

            # O(NoA)
            pathes = [(p.path, p.score) for p in pathfinders]
            m = max(pathes, key=lambda x: x[1])

            # O(1)
            self.pheromon_table.next_iteration()

            # O(V ** 2)
            for u, u1 in m[0].items():
                for v, v1 in m[0].items():
                    self.pheromon_table.add_update(u, u1, v, v1, 1 / (1 + self.best_score - m[1]))

        return GraphMap.construct_graph_map(self.best_choice, self.graph1, self.graph2)
