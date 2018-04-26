import pytest
import _pytest.outcomes

class ForceFailed(_pytest.outcomes.OutcomeException):
    __module__ = 'builtins'
    def __init__(self, msg=None, pytrace=True):
        _pytest.outcomes.OutcomeException.__init__(self, msg=msg, pytrace=pytrace)

def forcefail(msg="", pytrace=True):
    __tracebackhide__ = True
    raise ForceFailed(msg=msg, pytrace=pytrace)

class ForceFailEnabler(object):
    @pytest.mark.trylast
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        rep = outcome.get_result()
        if call.excinfo and call.excinfo.errisinstance(ForceFailed):
            rep.outcome = "failed"
            del rep.wasxfail

def pytest_configure(config):
    forcefailenabler = ForceFailEnabler()
    config.pluginmanager.register(forcefailenabler,'forcefailenabler')
