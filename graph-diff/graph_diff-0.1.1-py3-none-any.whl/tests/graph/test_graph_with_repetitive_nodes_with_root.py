import unittest

from graph_diff.graph import rnr_graph, lr_node
from graph_diff.graph.graph_with_repetitive_nodes_exceptions import GraphWithRepetitiveNodesKeyError


class GraphWithRepetitiveNodesWithRootTest(unittest.TestCase):
    def setUp(self):
        self.test_graph = rnr_graph()

    def test_add_node(self):
        self.assertFalse(lr_node(1, 1) in self.test_graph)
        self.test_graph.add_node(lr_node(1, 1))
        self.assertTrue(lr_node(1, 1) in self.test_graph)

    def test_add_edge(self):
        self.assertFalse(lr_node(1, 1) in self.test_graph)
        self.assertFalse(lr_node(1, 2) in self.test_graph)
        self.test_graph.add_edge(lr_node(1, 1), lr_node(1, 2))
        self.assertTrue(lr_node(1, 1) in self.test_graph)
        self.assertTrue(lr_node(1, 2) in self.test_graph)

    def test_add_edge_exp(self):
        self.assertFalse(lr_node(1, 1) in self.test_graph)
        self.assertFalse(lr_node(1, 2) in self.test_graph)
        self.assertRaises(GraphWithRepetitiveNodesKeyError,
                          self.test_graph.add_edge_exp,
                          lr_node(1, 1),
                          lr_node(1, 2))


if __name__ == '__main__':
    unittest.main()
