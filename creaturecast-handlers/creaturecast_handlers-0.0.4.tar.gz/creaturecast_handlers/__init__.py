__version__ = '0.0.4'
__description__ = 'Creaturecast Handlers'
__author__ = 'Paxton Gerrish'
__email__ = 'creaturecastlabs@gmail.com'
__url__ = 'https://github.com/Paxtongerrish/creaturecast_handlers.git'

import os
import json
import PySignal
import itertools

rig_settings_path = '%s/data/rig_settings.json' % os.path.dirname(__file__.replace('\\', '/'))
with open(rig_settings_path, mode='r') as f:
    rig_settings = json.load(f)


class NodeHandler(object):

    created = PySignal.ClassSignal()
    start_parent = PySignal.ClassSignal()
    end_parent = PySignal.ClassSignal()
    start_unparent = PySignal.ClassSignal()
    end_unparent = PySignal.ClassSignal()
    end_create = PySignal.ClassSignal()
    delete = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(NodeHandler, self).__init__()


class SelectionHandler(object):

    selection_changed = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(SelectionHandler, self).__init__()
        self.selected_nodes = set()

    def select_nodes(self, *nodes):
        self.selected_nodes = nodes
        self.selection_changed.emit(self.selected_nodes)


class UserHandler(object):

    user_changed = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(UserHandler, self).__init__()
        self.current_user = None

    def set_user(self, user):
        self.current_user = user
        self.user_changed.emit(user)


class ErrorHandler(object):

    error = PySignal.ClassSignal()

    def __init__(self, *args, **kwargs):
        super(ErrorHandler, self).__init__()


def create_alpha_dictionary(depth=4):
    ad = {}
    mit = 0
    for its in range(depth)[1:]:
        for combo in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=its):
            ad[mit] = ''.join(combo)
            mit += 1
    return ad


class NameHandler(object):

    alpha_dictionary = create_alpha_dictionary()

    def __init__(self):
        super(NameHandler, self).__init__()
        self.names = []

    def create_name_string(self, **kwargs):
        existing_name = kwargs.get('name', None)

        if existing_name:
            self.names.append(existing_name)
            return existing_name

        side = kwargs.get('side', None)
        index = kwargs.get('index', None)

        side_prefix = ''
        index_string = ''

        suffix = kwargs.get('suffix', None)
        root_name = kwargs.get('root_name', '')
        suffix_string = ''
        if suffix:
            suffix_string = '_%s' % suffix
        if side is not None:
            side_prefix = '%s_' % rig_settings['side_prefixes'][side]
        if index is not None:
            index_string = '_%s' % self.alpha_dictionary[index]

        name = '%s%s%s%s' % (
            side_prefix,
            root_name,
            index_string,
            suffix_string
        )

        if name in self.names:
            print 'The name "%s" already exists' % name

        if existing_name in self.names:
            self.names.remove(existing_name)

        self.names.append(name)

        return name

    def get_index_name(self, **kwargs):

        index = kwargs.get('index', None)
        index_string = ''
        root_name = kwargs.get('root_name')
        if index is not None:
            index_string = '_%s' % self.alpha_dictionary[index]

        index_name = '%s%s' % (
            root_name,
            index_string
        )

        return index_name


name_handler = NameHandler()
user_handler = UserHandler()
selection_handler = SelectionHandler()
node_handler = NodeHandler()
error_handler = ErrorHandler()
