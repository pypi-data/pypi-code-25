# -*- coding: utf-8 -*-
"""AsyncIO Service-based programming."""
# :copyright: (c) 2017, Robinhood Markets
#             All rights reserved.
# :license:   BSD (3 Clause), see LICENSE for more details.
import re
import sys
import typing
from typing import Any, Mapping, NamedTuple, Sequence

__version__ = '1.11.1'
__author__ = 'Robinhood Markets'
__contact__ = 'opensource@robinhood.com'
__homepage__ = 'https://github.com/fauststream/mode'
__docformat__ = 'restructuredtext'

# -eof meta-


class version_info_t(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: str


# bumpversion can only search for {current_version}
# so we have to parse the version here.
_temp = re.match(
    r'(\d+)\.(\d+).(\d+)(.+)?', __version__).groups()
VERSION = version_info = version_info_t(
    int(_temp[0]), int(_temp[1]), int(_temp[2]), _temp[3] or '', '')
del(_temp)
del(re)

if typing.TYPE_CHECKING:
    from .services import Service                         # noqa: E402
    from .signals import BaseSignal, Signal, SyncSignal   # noqa: E402
    from .supervisors import (                            # noqa: E402
        ForfeitOneForAllSupervisor,
        ForfeitOneForOneSupervisor,
        OneForAllSupervisor,
        OneForOneSupervisor,
        SupervisorStrategy,
        CrashingSupervisor,
    )
    from .types import ServiceT, SupervisorStrategyT      # noqa: E402
    from .types import BaseSignalT, SignalT, SyncSignalT  # noqa: E402
    from .utils.times import Seconds, want_seconds        # noqa: E402
    from .utils.logging import get_logger, setup_logging  # noqa: E402
    from .utils.objects import label, shortlabel          # noqa: E402
    from .worker import Worker                            # noqa: E402

__all__ = [
    'BaseSignal',
    'BaseSignalT',
    'Service',
    'Signal',
    'SignalT',
    'SyncSignal',
    'SyncSignalT',
    'ForfeitOneForAllSupervisor',
    'ForfeitOneForOneSupervisor',
    'OneForAllSupervisor',
    'OneForOneSupervisor',
    'SupervisorStrategy',
    'CrashingSupervisor',
    'ServiceT', 'SupervisorStrategyT',
    'Seconds', 'want_seconds',
    'get_logger', 'setup_logging',
    'label', 'shortlabel',
    'Worker',
]


# Lazy loading.
# - See werkzeug/__init__.py for the rationale behind this.
from types import ModuleType  # noqa

all_by_module: Mapping[str, Sequence[str]] = {
    'mode.services': ['Service'],
    'mode.signals': ['BaseSignal', 'Signal', 'SyncSignal'],
    'mode.supervisors': [
        'ForfeitOneForAllSupervisor',
        'ForfeitOneForOneSupervisor',
        'OneForAllSupervisor',
        'OneForOneSupervisor',
        'SupervisorStrategy',
        'CrashingSupervisor',
    ],
    'mode.types': [
        'BaseSignalT',
        'ServiceT',
        'SignalT',
        'SupervisorStrategyT',
        'SyncSignalT',
    ],
    'mode.utils.times': ['Seconds', 'want_seconds'],
    'mode.utils.logging': ['get_logger', 'setup_logging'],
    'mode.utils.objects': ['label', 'shortlabel'],
    'mode.worker': ['Worker'],
}

object_origins = {}
for module, items in all_by_module.items():
    for item in items:
        object_origins[item] = module


class _module(ModuleType):
    """Customized Python module."""

    def __getattr__(self, name: str) -> Any:
        if name in object_origins:
            module = __import__(
                object_origins[name], None, None, [name])
            for extra_name in all_by_module[module.__name__]:
                setattr(self, extra_name, getattr(module, extra_name))
            return getattr(module, name)
        return ModuleType.__getattribute__(self, name)

    def __dir__(self) -> Sequence[str]:
        result = list(new_module.__all__)
        result.extend(('__file__', '__path__', '__doc__', '__all__',
                       '__docformat__', '__name__', '__path__',
                       'VERSION', 'version_info_t', 'version_info',
                       '__package__', '__version__', '__author__',
                       '__contact__', '__homepage__', '__docformat__'))
        return result


# keep a reference to this module so that it's not garbage collected
old_module = sys.modules[__name__]

new_module = sys.modules[__name__] = _module(__name__)
new_module.__dict__.update({
    '__file__': __file__,
    '__path__': __path__,  # type: ignore
    '__doc__': __doc__,
    '__all__': tuple(object_origins),
    '__version__': __version__,
    '__author__': __author__,
    '__contact__': __contact__,
    '__homepage__': __homepage__,
    '__docformat__': __docformat__,
    '__package__': __package__,
    'version_info_t': version_info_t,
    'version_info': version_info,
    'VERSION': VERSION,
})
