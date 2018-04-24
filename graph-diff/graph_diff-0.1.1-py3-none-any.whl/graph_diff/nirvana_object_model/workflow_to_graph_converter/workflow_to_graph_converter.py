from abc import ABC, abstractmethod

from graph_diff.graph import GraphWithRepetitiveNodesWithRoot
from graph_diff.graph_diff_algorithm import GraphMap
from graph_diff.nirvana_object_model.workflow import Workflow
from graph_diff.nirvana_object_model.workflow_to_dot_converter import GraphDotColorer


class WorkflowToGraphConverter(ABC):
    """Interface for graph converter"""

    @abstractmethod
    def convert(self, workflow: Workflow) -> GraphWithRepetitiveNodesWithRoot: pass

    @abstractmethod
    def reverse_graph(self, graph: GraphWithRepetitiveNodesWithRoot) -> Workflow: pass

    @abstractmethod
    def convert_graph_map(self, graph_map: GraphMap) -> (Workflow, GraphDotColorer): pass
