"""
Module for nirvana workflow description.
Workflow is a set of blocks, that contain of operation and some options.
Operation is a id, input and ounput nests.
Blocks are connected with each other either by execution or by data.
If connection is through data it connects identical nest of two blocks,
one input and one output.
"""

from .block import Block
from .operation import Operation
from .workflow import Workflow
