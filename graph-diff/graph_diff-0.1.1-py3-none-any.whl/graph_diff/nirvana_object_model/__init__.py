"""
Module for usage of nirvana workflows.
Consists of
- workflow generator module
- workflow representation module
- converter to pydot format module
- converter to graph format module

Alongside pipeline class is provided.
The usage of the module is highly recommended through the Pipeline class.
When constructing it you may specify way of transformation of the workflow,
algorithm to be used, etc.

Workflow deserializer is used to get workflow objects from json representation.
"""

import graph_diff.nirvana_object_model.worflow_generator
import graph_diff.nirvana_object_model.workflow
import graph_diff.nirvana_object_model.workflow_to_dot_converter
import graph_diff.nirvana_object_model.workflow_to_graph_converter
from .pipeline import Pipeline
from .workflow_deserializer import deserialize
