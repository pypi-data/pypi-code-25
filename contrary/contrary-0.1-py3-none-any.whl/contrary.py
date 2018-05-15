"""
Contrary - Ordered data structures from multiple YAML sources.
    :copyright: (c) 2018 by Robert Bricheno.
    :license: MIT, see LICENSE for more details.
"""
import yaml
import yaml.resolver
import deepops
from collections import OrderedDict
from typing import List, Union, Callable


class Contrary:
    _data = None
    file_path = []

    @staticmethod
    def ordered_load(stream, yaml_loader: yaml.Loader = yaml.SafeLoader, object_pairs_hook: Callable = OrderedDict):
        """Creates a custom loader and uses it to load yaml into an ordered data structure based on OrderedDicts."""
        class OrderedLoader(yaml_loader):
            pass

        def construct_mapping(loader: yaml.Loader, node):
            loader.flatten_mapping(node)
            return object_pairs_hook(loader.construct_pairs(node))

        def bytestring_constructor(loader, node):
            """Read a node as if it was a byte string. Assume the contents are utf-8, and can be safely encoded into
               bytes. Now you can write YAML in your config files like:

                   value_name: !b abc123

               and get back:

                   value_name == b'abc123'"""
            value = loader.construct_scalar(node)
            return value.encode('utf-8')

        OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
        OrderedLoader.add_constructor('!b', bytestring_constructor)
        return yaml.load(stream, OrderedLoader)

    def __init__(self, file_path: Union[str, List, None]):
        """Load one or more files into an ordered data structure (made of lists, OrderedDicts and raw types).
           The first file loaded is the 'base' file into which subsequent files are merged using deepops"""
        assert file_path is not None
        my_class = self.__class__
        if my_class._data is None:
            if isinstance(file_path, str):
                my_class.file_path = [file_path, ]
                my_class._data = {}
                with open(file_path) as f:
                    my_class._data = my_class.ordered_load(f)
            else:
                assert type(file_path) is list
                assert len(file_path) > 0
                my_class.file_path = file_path
                my_class._data = {}
                with open(my_class.file_path[0]) as f1:
                    my_class._data = my_class.ordered_load(f1)
                for path in my_class.file_path[1:]:
                    with open(path) as f2:
                        temp_data = my_class.ordered_load(f2)
                        deepops.deepmerge(my_class._data, temp_data, list_as_set=True)

    @classmethod
    def reload(cls):
        """Reload the data from the file(s) on disk"""
        if cls.file_path is None:
            raise AssertionError("You must load the config once with a valid filename before forcing a reload")
        cls._data = None
        return cls(cls.file_path)

    def __setattr__(self, *_):
        raise AttributeError("Can't set attribute, you must reload the config file instead")

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        raise NotImplementedError("Cannot set data manually, you must use the loader methods")
