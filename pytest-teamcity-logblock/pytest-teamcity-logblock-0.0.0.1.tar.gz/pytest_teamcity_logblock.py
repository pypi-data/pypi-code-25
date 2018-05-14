import pytest

try:
    import teamcity
    teamcityAvailable = True
except ImportError:
    teamcityAvailable = False

class TeamCityLogBlockBuilder(object):
    def __init__(self):
        self.teamcity = teamcity.messages.TeamcityServiceMessages()

    @pytest.mark.trylast
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(self,item):
        self.teamcity.blockOpened('setup')
        yield
        self.teamcity.blockClosed('setup')

    @pytest.mark.trylast
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self,item):
        self.teamcity.blockOpened('call')
        yield
        self.teamcity.blockClosed('call')

    @pytest.mark.trylast
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_teardown(self,item):
        self.teamcity.blockOpened('teardown')
        yield
        self.teamcity.blockClosed('teardown')

@pytest.mark.trylast
def pytest_configure(config):
    captureOption = config.getoption("--capture")

    if teamcityAvailable:
        # https://github.com/JetBrains/teamcity-messages/blob/master/teamcity/pytest_plugin.py pytest_configure
        teamcityOption = teamcity.is_running_under_teamcity()
        if config.getoption("--teamcity")>=1:
            teamcityOption = True
        if config.getoption("--no-teamcity")>=1:
            teamcityOption = False
    else:
        teamcityOption = False

    if teamcityOption and (not captureOption or captureOption=='no'):
        config.pluginmanager.register(TeamCityLogBlockBuilder(), 'teamcitylogblockbuilder')

