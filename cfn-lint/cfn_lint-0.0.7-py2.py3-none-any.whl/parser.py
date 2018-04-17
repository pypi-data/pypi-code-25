"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Licensed under the Apache License, Version 2.0 (the "License").
  You may not use this file except in compliance with the License.
  A copy of the License is located at

      http://www.apache.org/licenses/LICENSE-2.0

  or in the "license" file accompanying this file. This file is distributed
  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
  express or implied. See the License for the specific language governing
  permissions and limitations under the License.
"""
import logging
import six
from yaml.composer import Composer
from yaml.reader import Reader
from yaml.scanner import Scanner
from yaml.resolver import Resolver
from yaml.parser import Parser
from yaml import ScalarNode
from yaml import SequenceNode
from yaml import MappingNode
from yaml.constructor import SafeConstructor

UNCONVERTED_SUFFIXES = ["Ref", "Condition"]
FN_PREFIX = "Fn::"

LOGGER = logging.getLogger(__name__)


def create_node_class(cls):
    """
    Create dynamic node class
    """
    class node_class(cls):
        """Node class created based on the input class"""
        def __init__(self, x, start_mark, end_mark):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)
            self.start_mark = start_mark
            self.end_mark = end_mark

        # pylint: disable=bad-classmethod-argument, unused-argument
        def __new__(self, x, start_mark, end_mark):
            return cls.__new__(self, x)
    node_class.__name__ = '%s_node' % cls.__name__
    return node_class


dict_node = create_node_class(dict)
list_node = create_node_class(list)
str_node = create_node_class(str)


class NodeConstructor(SafeConstructor):
    """
    Node Constructors for loading different types in Yaml
    """
    # To support lazy loading, the original constructors first yield
    # an empty object, then fill them in when iterated. Due to
    # laziness we omit this behaviour (and will only do "deep
    # construction") by first exhausting iterators, then yielding
    # copies.
    def construct_yaml_map(self, node):
        obj, = SafeConstructor.construct_yaml_map(self, node)
        return dict_node(obj, node.start_mark, node.end_mark)

    def construct_yaml_seq(self, node):
        obj, = SafeConstructor.construct_yaml_seq(self, node)
        return list_node(obj, node.start_mark, node.end_mark)

    def construct_yaml_str(self, node):
        obj = SafeConstructor.construct_yaml_str(self, node)
        assert isinstance(obj, str)
        return str_node(obj, node.start_mark, node.end_mark)


NodeConstructor.add_constructor(
    u'tag:yaml.org,2002:map',
    NodeConstructor.construct_yaml_map)

NodeConstructor.add_constructor(
    u'tag:yaml.org,2002:seq',
    NodeConstructor.construct_yaml_seq)

NodeConstructor.add_constructor(
    u'tag:yaml.org,2002:str',
    NodeConstructor.construct_yaml_str)


class MarkedLoader(Reader, Scanner, Parser, Composer, NodeConstructor, Resolver):
    """
    Class for marked loading YAML
    """
    # pylint: disable=non-parent-init-called,super-init-not-called
    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        SafeConstructor.__init__(self)
        Resolver.__init__(self)


def multi_constructor(loader, tag_suffix, node):
    """
    Deal with !Ref style function format
    """

    if tag_suffix not in UNCONVERTED_SUFFIXES:
        tag_suffix = "{}{}".format(FN_PREFIX, tag_suffix)

    constructor = None

    if tag_suffix == "Fn::GetAtt":
        constructor = construct_getatt
    elif isinstance(node, ScalarNode):
        constructor = loader.construct_scalar
    elif isinstance(node, SequenceNode):
        constructor = loader.construct_sequence
    elif isinstance(node, MappingNode):
        constructor = loader.construct_mapping
    else:
        raise "Bad tag: !{}".format(tag_suffix)

    return {tag_suffix: constructor(node)}


def construct_getatt(node):
    """
    Reconstruct !GetAtt into a list
    """

    if isinstance(node.value, six.text_type):
        return node.value.split(".")
    elif isinstance(node.value, list):
        return [s.value for s in node.value]
    else:
        raise ValueError("Unexpected node type: {}".format(type(node.value)))
