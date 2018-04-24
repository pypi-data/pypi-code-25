from .graph_generator import GraphGenerator
from .graph_with_repetitive_nodes_with_root import GraphWithRepetitiveNodesWithRoot, lr_node, rnr_graph


class StandardGraphGenerator(GraphGenerator):
    """Simplest algorithm that generates graphs"""

    def __init__(self,
                 min_node_num=2,
                 max_node_num=30,
                 node_number_expectation=None):
        self.min_node_num = min_node_num
        self.max_node_num = max_node_num
        if node_number_expectation is None:
            self.node_number_expectation = max_node_num * 0.3
        else:
            self.node_number_expectation = node_number_expectation

    def generate_graph(self):
        """
        Generates graph.

        Number of node has geometric distribution with
        node_number_expectation as its expectation.
        Labels have triangular distribution with
        (1, (node_number - 1) / 5, node_number) parameters.
        Edges between all nodes are generated with probability 1/2.
        :return:    graph
        """
        graph = rnr_graph()

        import numpy.random
        import math

        # Expectation is equal to self.node_number_expectation
        node_number = numpy.random.geometric(p=1 / self.node_number_expectation) + 1
        node_number = max(self.min_node_num, node_number)
        node_number = min(self.max_node_num, node_number)

        a_label_number = 1

        # Mode for number of labels is 20% of numbers of the nodes.
        mode_label_number = math.ceil((node_number - 1) / 5)
        b_label_number = node_number

        label_number = int(math.ceil(numpy.random.triangular(left=a_label_number,
                                                             mode=mode_label_number,
                                                             right=b_label_number)))

        node_labels = numpy.random.multinomial(n=node_number, pvals=[1 / label_number] * label_number)
        node_labels = [ls + 1 for ls in node_labels]

        for label, label_size in enumerate(node_labels):
            label += 1  # labels start from 1
            for i in range(1, label_size + 1):  # numbers start from 1
                new_node = lr_node(str(label), i)
                graph.add_node(new_node)
                for node in graph:
                    if 1 == numpy.random.randint(2) \
                            and node not in [new_node, GraphWithRepetitiveNodesWithRoot.ROOT]:
                        graph.add_edge_exp(from_node=node,
                                           to_node=new_node)

        return graph
