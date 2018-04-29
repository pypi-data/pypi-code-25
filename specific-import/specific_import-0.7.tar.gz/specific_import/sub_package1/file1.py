import os
import sys
import importlib.util


def get_absolute_path_of_file_doing_importing():
    path = os.path.realpath(sys.argv[0])
    return path


def get_absolute_directory_path_of_file_doing_importing():
    path = get_absolute_path_of_file_doing_importing()
    return os.path.dirname(path)


def define_path_relative_to_file_doing_importing(resource_file):
    path_to_directory_of_file_doing_importing = get_absolute_directory_path_of_file_doing_importing()
    relative_file_path_of_target_file = os.path.join(path_to_directory_of_file_doing_importing, resource_file)
    absolute_file_path_of_target_file = os.path.abspath(relative_file_path_of_target_file)
    return absolute_file_path_of_target_file


def define_path_based_on_resource_directory(resource_file, absolute_path_to_resource_directory):
    absolute_file_path_of_target_file = '{}/{}'.format(absolute_path_to_resource_directory, resource_file)
    return absolute_file_path_of_target_file


def module_is_already_loaded(absolute_file_path_of_target_file):
    return absolute_file_path_of_target_file in sys.modules


def add_module_to_global_modules(absolute_file_path_of_target_file, resource):
    sys.modules[absolute_file_path_of_target_file] = resource


def load_resource_as_module(resource, spec):
    spec.loader.exec_module(resource)


def import_file(resource_file, absolute_path_to_resource_directory=None):

    if absolute_path_to_resource_directory is None:
        absolute_file_path_of_target_file = define_path_relative_to_file_doing_importing(resource_file)
    else:
        absolute_file_path_of_target_file = define_path_based_on_resource_directory(
            resource_file, 
            absolute_path_to_resource_directory
        )

    spec = importlib.util.spec_from_file_location('', absolute_file_path_of_target_file)
    resource = importlib.util.module_from_spec(spec)

    if module_is_already_loaded(absolute_file_path_of_target_file):
        return sys.modules[absolute_file_path_of_target_file]

    load_resource_as_module(resource, spec)
    add_module_to_global_modules(absolute_file_path_of_target_file, resource)
    return resource

