from abc import ABC, abstractmethod

from .graph_with_repetitive_nodes_with_root import GraphWithRepetitiveNodesWithRoot


class GraphGenerator(ABC):
    """
    Interface for generator of graphs.
    """

    @abstractmethod
    def generate_graph(self) -> GraphWithRepetitiveNodesWithRoot: pass
