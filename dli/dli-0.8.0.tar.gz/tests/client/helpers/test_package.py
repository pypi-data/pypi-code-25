import logging

from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import sentinel

from dli.client.helpers import package

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class TestPackage(TestCase):
    def test_get_packages(self):
        pkg = MagicMock()
        datasets = MagicMock()

        expected = [sentinel.d1, sentinel.d2]

        pkg.package_datasets.return_value = datasets
        datasets.get_entities.return_value = expected

        result = package.get_datasets(pkg)

        pkg.package_datasets.assert_called_once()
        datasets.get_entities.assert_called_once_with('dataset')

        self.assertListEqual(expected, result)
