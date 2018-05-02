from typing import Iterable
from enum import Enum


class PartitionKeys(Enum):
    TRAIN = 'train'
    DEVELOP = 'develop'
    TEST = 'test'
    EVALUATE = 'evaluate'


class DatasetPartition:
    def ids(self, name) -> Iterable[int]:
        raise NotImplementedError

    def partitions(self) -> Iterable[str]:
        raise NotImplementedError


class Train80(DatasetPartition):
    def __init__(self, dataset, partition=None):
        """
        `dataset` Dataset object, with dataset.size property.
        `partition` str, name of partition
        """
        nb_train = int(dataset.size * 0.8)
        nb_test = dataset.size - nb_train
        self._ids_train = range(nb_train)
        self._ids_test = range(nb_train, dataset.size)

    def ids(self, name) -> Iterable[int]:
        return {'train': self._ids_train, 'test': self._ids_test}[name]

    def partitions(self):
        return ('train', 'test')


class ExplicitIds(DatasetPartition):
    def __init__(self, ids_dict: dict):
        self._ids_dict = ids_dict

    def ids(self, name) -> Iterable[int]:
        return tuple(self._ids_dict[name])

    def partitions(self):
        return tuple(self._ids_dict.keys())