__version__ = '0.0.4'
__description__ = 'Base node for creaturecast'
__author__ = 'Paxton Gerrish'
__email__ = 'creaturecastlabs@gmail.com'
__url__ = 'https://github.com/Paxtongerrish/creaturecast_node.git'


import json
import copy
import uuid
import creaturecast_handlers as hdr

all_nodes = dict()


class Node(object):
    """
    An abstract data container
    Can be organized hierarchically
    """

    inherited_data = ['size', 'root_name', 'side', 'index']
    invalid_keyword_args = ['created']

    default_data = dict(
        size=1.0,
        side=2,
        root_name='node',
        created=False,
        layer='node'
    )

    def __copy__(self):
        raise Exception('%s\'s are not copyable' % self.__class__.__name__)

    def __eq__(self, other):
        if other.__class__ == self.__class__:
            if self.data['uuid'] == other.data['uuid']:
                return True
        return False

    def __str__(self):
        if self.data.get('name', None):
            return '<%s "%s">' % (self.__class__.__name__, self.data['name'])
        return '<%s>' % self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    def __delete__(self):
        all_nodes.pop(self.data['uuid'], None)

        self.unparent()
        hdr.name_handler.names.remove(self.data['name'])
        hdr.node_handler.delete.emit(self)
        #for child in self.children:
        #    child.__delete__()

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__()

        for arg in self.invalid_keyword_args:
            kwargs.pop(arg, None)

        if args and isinstance(args[0], Node):
            data = args[0].data
            data.update(kwargs)
            kwargs = data

        self.m_object_handle = None
        self.database_object = kwargs.pop('database_object', None)
        self.parent = None
        self.children = []
        self.nodes = dict()

        parent = kwargs.pop('parent', None)

        for key in self.inherited_data:
            if key not in kwargs and parent and key in parent.data:
                kwargs[key] = parent.data[key]

        data = extract_default_data(self.__class__)
        data.update(kwargs)
        data['uuid'] = str(uuid.uuid4())
        data['class_type'] = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        data['name'] = hdr.name_handler.create_name_string(**data)
        self.data = JsonDict(serializable_check=True, **data)

        self.set_parent(parent)

        self.nodes = Nodes(self)
        self.plug_dictionary = dict()
        self.plugs = Plugs(self)

        all_nodes[self.data['uuid']] = self

    def get_position(self):
        """
        "get_position" Creates a list of integers that represent this nodes place in the scene hierarchy
        :return int list:
        """
        position = []
        parent = self.parent
        node = self
        while parent:
            position.insert(0, parent.children.index(node))
            node = parent
            parent = parent.parent
        return position

    def create_plug(self, name, **kwargs):
        kwargs['name'] = name
        plug = Plug(self, **kwargs)
        plug.data['create'] = True
        self.plug_dictionary[name] = plug
        return plug

    def set_parent(self, parent):
        """
        Hooks into callbacks related to setting parents
        """
        if self == parent:
            hdr.error_handler.error.emit('Cannot parent %s to itself' % self.data['name'])
        elif parent in self.get_descendants():
            hdr.error_handler.error.emit('Cannot parent %s to one of its children' % self.data['name'])
            self.unparent()

        if parent:
            hdr.node_handler.start_parent.emit(self, parent)

            self.parent = parent
            self.data['parent_id'] = parent.data['uuid']
            parent.children.append(self)

            hdr.node_handler.end_parent.emit(self, parent)

    def unparent(self):
        """
        Hooks into callbacks related to un-parenting nodes
        """
        if self.parent:
            hdr.node_handler.start_unparent.emit(self)
            if self.parent:
                self.parent.children.remove(self)
            self.parent = None
            hdr.node_handler.end_unparent.emit(self)

    def delete(self):
        self.__delete__()

    def get_descendants(self, node_type=None):
        descendants = []
        for child in self.get_children(node_type=node_type):
            descendants.append(child)
            descendants.extend(child.get_descendants(node_type=node_type))
        return descendants

    def get_children(self, node_type=None):
        if node_type is None:
            return self.children
        return [x for x in self.children if isinstance(x, node_type)]

    def insert_child(self, index, child):
        child.unparent()
        if child:
            child.parent = self
            self.children.insert(index, self)

    def get_index(self):
        if self.parent and self in self.parent.children:
            return self.parent.children.index(self)
        return 0

    def get_controller(self):
        return self.get_root().controller

    def get_root(self):
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    def get_long_name(self):
        nodes = self.get_descendants()
        nodes.append(self)
        return '|%s' % ('|'.join(nodes))

    def get_index_name(self):
        return hdr.name_handler.get_index_name(**self.data)

    def create_child(self, **kwargs):
        kwargs['parent'] = self
        return self.__class__(**kwargs)

    def get_short_name(self):
        return hdr.name_handler.get_short_name(**self.data)

    def create(self):

        """
        "create" provides dual functionality of:
            -creating MObjects for maya nodes
            -building the structure of parts (rigs).
        """
        if self.data['created']:
            raise Exception('%s has already been created.' % self)

        hdr.node_handler.created.emit(self)
        self.data['created'] = True
        return self


class Nodes(dict):

    def __init__(self, node):
        super(Nodes, self).__init__()
        self.node = node

    def get(self, *args, **kwargs):
        recursive = kwargs.get('recursive', False)
        instance_type = kwargs.get('instance_type', None)
        if kwargs.get('recursive', False):
            nodes = super(Nodes, self).get(*args)
            if instance_type:
                nodes = [x for x in nodes if isinstance(x, instance_type)]
            child_nodes = []
            for node in nodes:
                if args[0] in node.nodes:
                    child_nodes.extend(node.nodes.get(
                        recursive=recursive,
                        instance_type=instance_type,
                        *args
                    ))
            nodes.extend(child_nodes)
            return nodes
        else:
            return super(Nodes, self).get(*args)


class Plugs(object):
    def __init__(self, owner):
        super(Plugs, self).__init__()
        self.owner = owner
        self.current = 0

    def __getitem__(self, key):
        if key in self.owner.plug_dictionary:
            return self.owner.plug_dictionary[key]
        plug = Plug(self.owner, name=key)
        self.owner.plug_dictionary[key] = plug
        return plug

    def set_values(self, **kwargs):
        for key in kwargs:
            self[key].set_value(kwargs[key])


class Plug(object):

    default_data = dict(
        create=False,
        name='PLUG',
        value=None
    )

    def __init__(self, *args, **kwargs):

        super(Plug, self).__init__()
        if not isinstance(kwargs.get('name', None), basestring):
            raise Exception('Plug name invalid : "%s"' % kwargs.get('name', None))

        self.node = args[0]
        self.data = copy.copy(self.default_data)
        self.data.update(kwargs)
        self.incoming = None
        self.outgoing = []

    def __str__(self):
        return str(self.data['name'])

    def __repr__(self):
        return self.__str__()

    @property
    def value(self):
        return self.data.get('value', None)

    @value.setter
    def value(self, value):
        self.data['value'] = value

    def set_value(self, value):
        self.value = value

    def connect_to(self, *args):
        for plug in args:
            self.outgoing.append(plug)
            plug.incoming = self


class JsonDict(dict):
    """
    A Dictionary-Like object that checks that data is json serializable
    """

    def __init__(self, serializable_check=True, *args, **kwargs):
        super(JsonDict, self).__init__(*args, **kwargs)
        self.serializable_check = serializable_check

    def __setitem__(self, key, value):
        if self.serializable_check:
            try:
                json.dumps(value)
            except TypeError, e:
                raise TypeError('Unable to serialize value.%s' % e.message)
        super(JsonDict, self).__setitem__(key, value)


def extract_default_data(class_object):
    data = dict()
    if hasattr(class_object, 'default_data'):
        data = copy.copy(class_object.default_data)
    for base_class in class_object.__bases__:
        base_data = extract_default_data(base_class)
        base_data.update(data)
        data = base_data
    return data


def get_rig_data(node):
    data = [serialize_node(node)]
    for part in node.nodes['parts']:
        data.append(serialize_node(part))
    return data


def serialize_node(node):
    node_data = dict(node.data)
    if node.parent:
        node_data['parent'] = node.parent.data['uuid']
    return node_data


def serialize_nodes(*nodes):
    for x in nodes:
        yield serialize_node(x)
        for y in x.get_descendants():
            yield serialize_node(y)


scene_root = Node(name='root')
all_nodes[scene_root.data['uuid']] = scene_root

def deserialize_node(data):
    parent_uuid = data.pop('parent', None)
    if parent_uuid in all_nodes:
        data['parent'] = all_nodes[parent_uuid]
    else:
        data['parent'] = scene_root

    class_tokens = data['class_type'].split('.')
    module = __import__('.'.join(class_tokens[0:-1]), fromlist=['.'])
    new_node = module.__dict__[class_tokens[-1]](**data)
    all_nodes[data['uuid']] = new_node
    return new_node


def deserialize_nodes(*args):
    for data in args:
        yield deserialize_node(data)

