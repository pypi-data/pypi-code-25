"""
Module for generation workflows.

All generators have the same interface.
"""

from .chain_workflow_generator import ChainWorkflowGenerator
from .similar_workflow_generator import SimilarWorkflowGenerator
from .standard_workflow_generator import StandardWorkflowGenerator
from .workflow_generator import WorkflowGenerator
