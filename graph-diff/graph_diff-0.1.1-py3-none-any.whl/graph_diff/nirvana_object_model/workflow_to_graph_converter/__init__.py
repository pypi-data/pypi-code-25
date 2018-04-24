"""
Module for converting workflows to simple graphs.
All converters have one interface.
Currently there are two converters: one is fully reversible, one not
(but a lot way faster).
"""

from .complete_workflow_to_graph_converter import CompleteWorkflowToGraphConverter
from .simple_workflow_to_graph_converter import SimpleWorkflowToGraphConverter
from .workflow_to_graph_converter import WorkflowToGraphConverter
