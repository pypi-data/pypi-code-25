from unittest import TestCase
from unittest.mock import MagicMock
from dli.client.helpers import dataset
from unittest.mock import sentinel
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class TestDataset(TestCase):
    def test_register_dataset(self):
        dataset_entity = MagicMock()
        _self = MagicMock()

        dataset_entity.self.return_value = _self
        _self.delete_dataset.return_value = sentinel.res

        result = dataset.unregister(dataset_entity)

        dataset_entity.self.assert_called_once()
        _self.delete_dataset.assert_called_once()

        self.assertIs(sentinel.res, result)