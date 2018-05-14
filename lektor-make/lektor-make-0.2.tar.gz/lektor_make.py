"""
Simple Lektor build plugin to run `make lektor` when watched files change

>>> import subprocess
>>> def wait():
...     wait.called = True
>>> def mock(cmd):
...     assert cmd == ['make', 'lektor']
...     return mock
>>> mock.wait = wait
>>> setattr(subprocess, 'Popen', mock)
>>> import lektor_make
>>> plugin = lektor_make.MakePlugin(lambda: None, None)
>>> plugin.on_before_build_all(lambda: None)
>>> mock.wait.called
True
"""

import subprocess
from lektor.pluginsystem import Plugin

class MakePlugin(Plugin):
    """Plugin"""
    name = 'make'
    description = 'Run `make lektor` for custom build systems.'
    cmd = ['make', 'lektor']

    def on_before_build_all(self, builder, **extra):
        """Even hook triggered before the other Lektor build steps"""
        subprocess.Popen(self.cmd).wait()
