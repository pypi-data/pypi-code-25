from abc import ABC, abstractmethod

from graph_diff.graph import GraphWithRepetitiveNodesWithRoot
from .graph_map import GraphMap


class GraphDiffAlgorithm(ABC):
    """Graph difference algorithm interface"""

    @abstractmethod
    def construct_diff(self,
                       graph1: GraphWithRepetitiveNodesWithRoot,
                       graph2: GraphWithRepetitiveNodesWithRoot) -> GraphMap: pass


class GraphDiffAlgorithmWithInit(GraphDiffAlgorithm):
    """
    Graph difference algorithm interface,
    that requires initial solution
    """

    @abstractmethod
    def set_init(self, new_init: GraphMap) -> GraphDiffAlgorithm: pass
