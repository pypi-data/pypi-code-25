# coding: utf-8

import os
import codecs
import pickle
from cachetools import LRUCache

from mlang.config import MODEL_LM_BERKELEYLM_DIR


def iter_file(file_path):
    with codecs.open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield line


def write_file(lines, file_path, mode='w'):
    with codecs.open(file_path, mode, encoding='utf-8') as f:
        f.writelines(lines)


def save_obj(obj, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)


def read_obj(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def get_sub_cls(super_cls, sub_cls_name):
    for sub_cls in super_cls.__subclasses__():
        if sub_cls_name == sub_cls.__name__:
            return sub_cls
    return None


class ClsGet(object):
    _INSTANCE = None

    @classmethod
    def get(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls()
        return cls._INSTANCE


_cache = LRUCache(maxsize=10)


def put_cache(name, obj):
    _cache[name] = obj


def get_cache(name):
    return _cache.get(name)


def clear_cache():
    _cache.clear()
