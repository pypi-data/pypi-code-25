from abc import ABC, abstractmethod

from graph_diff.nirvana_object_model.workflow import Workflow


class WorkflowGenerator(ABC):
    """Workflow generator interface"""

    @abstractmethod
    def generate_workflow(self) -> Workflow: pass
