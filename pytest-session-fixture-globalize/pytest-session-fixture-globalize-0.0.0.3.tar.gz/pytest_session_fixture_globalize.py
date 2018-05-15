### pytest-session-fixture-globalize (C) @cielavenir (BSD License)
### if you want to use this feature without explicit enabling, you can embed this module into your conftest.py.
### in such cases, this header must be retained.

import os.path
import pytest
from _pytest.fixtures import FixtureManager

def __parsefactories__(self, *args, **kwargs):
    self.parsefactories_real(*args,**kwargs)
    for k in self._arg2fixturedefs:
        flist = self._arg2fixturedefs[k]
        session_test_list = set()
        for i,e in enumerate(flist):
            if e.scope!='session':
                continue
            if '.py' in e.baseid:
                e.baseid=os.path.dirname(e.baseid)
            key = tuple([e.argname,e.baseid])
            if key in session_test_list:
                flist[i]=None
            else:
                session_test_list.add(key)
        for i in range(len(flist)-1,-1,-1):
            if flist[i] is None: flist.pop(i)
        self._arg2fixturedefs[k] = flist

def pytest_addoption(parser):
    parser.addoption("--session-fixture-globalize", action='store_true', help="make session fixtures behave as if written in conftest, even if it is written in some modules")

def pytest_configure(config):
    if getattr(config.option,"session_fixture_globalize",False) or os.environ.get("PYTEST_SESSION_FIXTURE_GLOBALIZE"):
        if 'parsefactories_real' not in FixtureManager.__dict__:
            FixtureManager.parsefactories_real = FixtureManager.parsefactories
            FixtureManager.parsefactories = __parsefactories__

def pytest_unconfigure(config):
    if 'parsefactories_real' in FixtureManager.__dict__:
        FixtureManager.parsefactories = FixtureManager.parsefactories_real
        del FixtureManager.parsefactories_real
