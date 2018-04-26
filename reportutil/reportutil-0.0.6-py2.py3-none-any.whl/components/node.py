# encoding: utf-8

import logging_helper
from future.utils import with_metaclass
from abc import ABCMeta, abstractmethod, abstractproperty
from .._config import register_report_config
from .._constants import ReportConstant

logging = logging_helper.setup_logging()


class ReportNode(with_metaclass(ABCMeta, object)):

    """ This is the base class for all report nodes. """

    def __init__(self,
                 parent=None,
                 name=None,  # Can be none for a root node
                 *args,
                 **kwargs):

        self._parent = parent
        self._name = name
        self._cfg = register_report_config()

        # Setup structure for this node
        try:
            # Check whether node registered
            node = self._cfg[self.key]
            assert self.type == node[ReportConstant.node_type]

        except KeyError:
            # If not registered register node
            self._cfg[self.key] = {
                ReportConstant.node_type: self.type
            }

        except AssertionError:
            raise TypeError(u'Existing definition does not match node definition! '
                            u'{exist} != {new}'.format(exist=self.type,
                                                       new=self._cfg[self.key][ReportConstant.node_type]))

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    @property
    def key(self):

        """ Return the config registration key for this node """

        node_key = u'{cfg}.{key}'.format(cfg=ReportConstant.config.key,
                                         key=ReportConstant.config_properties.structure)

        if self.name is not None:
            if self.parent is not None:
                node_key = self.parent.key

            node_key = u'{root}.{node}'.format(root=node_key,
                                               node=self.name)

        return node_key

    @abstractproperty
    def type(self):

        """ Return one of ReportConstant.types """

        pass

    @abstractproperty
    def path(self):

        """ Fully qualified path to this node """

        pass

    @abstractmethod
    def generate(self):

        """ Generates the report node, creating this node and any children of this node.

        :return: path to report node index file.
        """

        pass

    @abstractmethod
    def remove(self):

        """ Deletes the report node, removing this node and any children of this node. """

        pass

    def move(self,
             location=None):

        """ Moves the report node to new location including any children of this node.

        :param location:    (node object) Moves this node to be a child of the passed node object.
                                          This includes updating the filesystem location.
        """

        # Validate destination (ensure a node with the same key as this is not already registered at location)
        self.validate_parent(location)

        # Move the report files to new location
        self._move_files(location=location.path)

        # Remove this node from current parent
        del self.parent.children[self.type][self]

        # Add this node to new parent
        location.children[self.type].append(self)

        # Update parent reference for this node to new parent
        self._parent = location

    @abstractmethod
    def _move_files(self,
                    location=None):

        """ Moves the report node to new location including any children of this node.

        :param location:    (string) Moves this root node to new filesystem location.
        """

        pass

    def validate_parent(self,
                        parent):

        """ Validate whether this node can be moved to new parent node.

        :param parent:    (node object) Parent node to validate.
        """

        matches = [node for node in parent.children[self.type] if node.key == self.key]

        if bool(matches):
            raise KeyError(u'This parent already has a node '
                           u'registered with this key ({node})'.format(node=self.key))
