from django.conf import settings
from django.test.runner import DiscoverRunner as TestRunnerBase


class TestRunner(TestRunnerBase):
    def setup_test_environment(self, **kwargs):
        super(TestRunner, self).setup_test_environment(**kwargs)
        settings.TESTING = True

    def teardown_test_environment(self, **kwargs):
        super(TestRunner, self).teardown_test_environment(**kwargs)
        settings.TESTING = True
