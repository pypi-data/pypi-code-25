# encoding: utf-8

import attr

# Get module version
from ._metadata import __version__

# Import key items from module
from .report import Report
from .components import ReportDirNode, ReportFileNode
from .nodes import HTMLReport
from ._constants import ReportConstant
from ._exceptions import ReportingError


@attr.s
class _ReportNodeTypes(object):
    # Base node types
    root = attr.ib(default=Report, init=False)
    dir = attr.ib(default=ReportDirNode, init=False)
    file = attr.ib(default=ReportFileNode, init=False)

    # Node file types
    html = attr.ib(default=HTMLReport, init=False)


ReportNodeTypes = _ReportNodeTypes()


__all__ = [
    Report,
    ReportConstant,
    ReportDirNode,
    ReportFileNode,
    ReportNodeTypes,
    HTMLReport,
    ReportingError
]
