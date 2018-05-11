"""Data structure to represent Sankey diagram data.

Author: Rick Lupton
Created: 2018-01-15
"""

import json
import attr
from collections import defaultdict

try:
    from ipysankeywidget import SankeyWidget
    from ipywidgets import Layout, Output, VBox
    from IPython.display import display, clear_output
except ImportError:
    SankeyWidget = None

_validate_opt_str = attr.validators.optional(attr.validators.instance_of(str))


def _convert_ordering(layers):
    """Wrap nodes in a single band, if none are specified."""
    for item in layers:
        if any(isinstance(x, str) for x in item):
            return tuple((tuple(layer_nodes), ) for layer_nodes in layers)

    return tuple(tuple(tuple(band_nodes) for band_nodes in layer_bands)
                 for layer_bands in layers)


def _validate_direction(instance, attribute, value):
    if value not in 'LR':
        raise ValueError('direction must be L or R')


@attr.s(slots=True, frozen=True)
class SankeyData(object):
    nodes = attr.ib()
    links = attr.ib()
    groups = attr.ib(default=attr.Factory(list))
    ordering = attr.ib(convert=_convert_ordering, default=[[]])
    dataset = attr.ib(default=None)

    def to_json(self):
        """Convert data to JSON-ready dictionary."""
        data = {
            'format': {'major': 0, 'minor': 1},
            'metadata': {
                'title': 'A Sankey diagram',
                'authors': [],
                'layers': self.ordering,
            },
            'nodes': [n.to_json() for n in self.nodes],
            'links': [l.to_json() for l in self.links],
            'groups': self.groups,
        }

        return data


@attr.s(slots=True, frozen=True)
class SankeyNode(object):
    id = attr.ib(validator=attr.validators.instance_of(str))
    title = attr.ib(default=None, validator=_validate_opt_str)
    direction = attr.ib(validator=_validate_direction, default='R')
    hidden = attr.ib(default=False)
    style = attr.ib(default=None, validator=_validate_opt_str)

    def to_json(self):
        """Convert node to JSON-ready dictionary."""
        return {
            'id': self.id,
            'title': {
                'label': self.title if self.title is not None else self.id
            },
            'style': {
                'direction': self.direction.lower(),
                'hidden': self.hidden is True or self.title == '',
                'type': self.style if self.style is not None else 'default',
            },
        }


def _validate_opacity(instance, attr, value):
    if not isinstance(value, float):
        raise ValueError('opacity must be a number')
    if value < 0 or value > 1:
        raise ValueError('opacity must be between 0 and 1')


@attr.s(slots=True, frozen=True)
class SankeyLink(object):
    source = attr.ib(validator=attr.validators.instance_of(str))
    target = attr.ib(validator=attr.validators.instance_of(str))
    type = attr.ib(default=None, validator=_validate_opt_str)
    time = attr.ib(default=None, validator=_validate_opt_str)
    value = attr.ib(default=0.0)
    title = attr.ib(default=None, validator=_validate_opt_str)
    color = attr.ib(default=None, validator=_validate_opt_str)
    opacity = attr.ib(default=1.0, convert=float, validator=_validate_opacity)
    original_flows = attr.ib(default=attr.Factory(list))

    def to_json(self):
        """Convert link to JSON-ready dictionary."""
        return {
            'source': self.source,
            'target': self.target,
            'type': self.type or '',
            # 'title': self.title,
            # 'time': self.time,
            'data': {
                'value': self.value,
            },
            'style': {
                'color': self.color,
                'opacity': self.opacity,
            }
        }
