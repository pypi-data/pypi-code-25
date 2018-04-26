# encoding: utf-8

import os
import logging_helper
from copy import deepcopy
from shutil import copytree, rmtree
from fdutil.path_tools import ensure_path_exists
from .._constants import ReportConstant
from .._exceptions import ReportingError
from .node import ReportNode

logging = logging_helper.setup_logging()


class ReportDirNode(ReportNode):

    """ The ReportDirNode object represents a single directory in the report structure.
        The represented directory can contain more ReportDirs or Report Files (i.e HTMLReport objects).
        A report directory should also contain an index file as this will be used as the primary access
        point to the report directory.

    """

    def __init__(self,
                 *args,
                 **kwargs):

        super(ReportDirNode, self).__init__(*args, **kwargs)

        # Initialise child tracking object
        self._child_nodes = deepcopy(ReportConstant.node_template)

    @property
    def type(self):
        return ReportConstant.types.dir

    @property
    def path(self):
        return os.path.join(self.parent.path,
                            self.name)

    @property
    def children(self):
        return self._child_nodes

    @property
    def child_dirs(self):
        return self.children.get(ReportConstant.types.dir, [])

    @property
    def child_files(self):
        return self.children.get(ReportConstant.types.file, [])

    def add_child(self,
                  name,
                  node_class,
                  *args,
                  **kwargs):

        # We create the node no matter what as we need it instantiated to check the type.
        obj = node_class(parent=self,
                         name=name,
                         *args,
                         **kwargs)

        obj.validate_parent(self)

        self.children[obj.type].append(obj)

        return obj

    def delete_child(self):
        # TODO: Delete child node
        raise NotImplementedError(u'delete_child method not written yet for dir nodes!')

    def get_child(self,
                  name):
        # TODO: Retrieve and return the requested report node object
        raise NotImplementedError(u'get_node method not written yet!')

    def generate_children(self):

        """ Invokes the generate methods on all children. """

        for d in self.child_dirs:
            d.generate()

        for f in self.child_files:
            f.generate()

    def generate(self):

        """ Generates the report node, creating this node and any children of this node.

        :return: path to report node index file.
        """

        # Generate this directory
        ensure_path_exists(self.path)

        # TODO: Generate index

        # Generate Children
        self.generate_children()

    def remove(self):
        # TODO: Delete node
        raise NotImplementedError(u'delete method not written yet for dir nodes!')

    def _move_files(self,
                    location=None):

        """ Moves the report node to new location including any children of this node.

        :param location:    (string) Moves this root node to new filesystem location.
        """

        if os.path.isdir(location):
            # TODO: how do we handle existing dir at new location?
            raise ReportingError(u'location dir already exists ({d})'.format(d=location))

        try:
            # Copy report structure to new location
            copytree(
                self.path,
                location,
                symlinks=True
            )

        except Exception as err:
            logging.error(u'Something went wrong moving the Report root node: {err}'.format(err=err))

            # Remove any files copied to new location
            rmtree(location)

            # Raise error up
            raise err

        else:
            # Remove old report location
            rmtree(self.path)

    def _load_node_config(self):

        """ Loads any children registered in config structure.

            Note: This will just create an object from the config,
                  it will not include anything added to the body!

        """

        node = self._cfg[self.key]

        for child_key, child in node:
            pass
            # TODO: How do we know which node type to instantiate -> _type=file but what kind? HTML?
            # TODO: Do we need a sub_type for nodes to specify this? e.g. sub_type=html
            # TODO: When we instantiate: we need to call self.add_child

        # TODO: Write this!
