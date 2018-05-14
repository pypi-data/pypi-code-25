from django.core.management import call_command
from django.test.testcases import TestCase, TransactionTestCase


class DataModelsTestCaseMixin(object):
    datamodels = []

    def setUp(self):
        if not isinstance(self, TestCase) and isinstance(self, TransactionTestCase):
            self.loaddata()

        super(DataModelsTestCaseMixin, self).setUp()

    @classmethod
    def setUpClass(cls):
        super(DataModelsTestCaseMixin, cls).setUpClass()
        if issubclass(cls, TestCase):
            cls.loaddata()

    @classmethod
    def loaddata(cls):
        if cls.datamodels:
            verbosity = getattr(cls, 'verbosity', 0)
            call_command('datamodels_loaddata', *cls.datamodels, verbosity=verbosity)
