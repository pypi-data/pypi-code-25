__version__ = '0.0.1'
__description__ = 'Creaturecast environment'
__author__ = 'Paxton Gerrish'
__email__ = 'creaturecastlabs@gmail.com'
__url__ = 'https://github.com/Paxtongerrish/creaturecast_environment.git'

import os
import json
import copy
from os.path import expanduser
import creaturecast_designer
import PySignal
import itertools

home_directory = expanduser("~").replace('\\', '/')
local_user = os.getenv('USER')
creaturecast_directory = '%screaturecast' % home_directory
package_directory = os.path.dirname(creaturecast_designer.__file__.replace('\\', '/'))
modules_directory = '%s/modules' % creaturecast_directory

if not os.path.exists(creaturecast_directory):
    os.makedirs(creaturecast_directory)


def create_alpha_dictionary(depth=4):
    ad = {}
    mit = 0
    for its in range(depth)[1:]:
        for combo in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=its):
            ad[mit] = ''.join(combo)
            mit += 1
    return ad


alpha_dictionary = create_alpha_dictionary()


class VariablesBase(object):
    def __init__(self, name, **kwargs):
        super(VariablesBase, self).__init__()

        self.local_path = '%s/%s.json' % (
            creaturecast_directory,
            name
        )
        self.package_path = '%s/data/%s.json' % (
            os.path.dirname(__file__.replace('\\', '/')),
            name
        )

        self.variables = dict()
        if os.path.exists(self.local_path):
            with open(self.local_path, mode='r') as f:
                file_contents = f.read()
            if file_contents:
                self.variables = json.loads(file_contents)
        else:
            with open(self.package_path, mode='r') as f:
                json_string = f.read()
                self.variables = json.loads(json_string)
            with open(self.local_path, mode='w') as f:
                f.write(json_string)

    def write_to_disk(self):
        with open(self.local_path, mode='w') as f:
            json_string = json.dumps(
                self.variables,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )

            f.write(json_string)

    def __getitem__(self, item):
        return copy.copy(self.variables[item])

    def __setitem__(self, key, value):
        self.variables[key] = copy.copy(value)
        self.write_to_disk()

    def get(self, *args, **kwargs):
        return self.variables.get(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.variables.update(*args, **kwargs)
        self.write_to_disk()



class EnvironmentVariables(VariablesBase):
    def __init__(self, *args, **kwargs):
        super(EnvironmentVariables, self).__init__()
        self.variables_path = '%s/environment_variables.json' % creaturecast_directory
        self.variables = dict()
        if os.path.exists(self.variables_path):
            with open(self.variables_path, mode='r') as f:
                file_contents = f.read()
            if file_contents:
                self.variables = json.loads(file_contents)

    def write_to_disk(self):
        with open(self.variables_path, mode='w') as f:
            json_string = json.dumps(
                self.variables,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )

            f.write(json_string)

    def __getitem__(self, item):
        return copy.copy(self.variables[item])

    def __setitem__(self, key, value):
        self.variables[key] = copy.copy(value)
        self.write_to_disk()

    def get(self, *args, **kwargs):
        return self.variables.get(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.variables.update(*args, **kwargs)
        self.write_to_disk()


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


class NameHandler(object):

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
            index_string = '_%s' % alpha_dictionary[index]

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

    @staticmethod
    def get_index_name(**kwargs):

        index = kwargs.get('index', None)
        index_string = ''
        root_name = kwargs.get('root_name')
        if index is not None:
            index_string = '_%s' % alpha_dictionary[index]

        index_name = '%s%s' % (
            root_name,
            index_string
        )

        return index_name


environment_variables = VariablesBase('environment_variables')
handle_shapes = VariablesBase('handle_shapes')
rig_settings = VariablesBase('rig_settings')

user_handler = UserHandler()
selection_handler = SelectionHandler()
node_handler = NodeHandler()
name_handler = NameHandler()
error_handler = ErrorHandler()
