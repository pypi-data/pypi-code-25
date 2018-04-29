import os
import sys
import inspect
import importlib.util


def get_absolute_path_of_file_doing_importing(frames):

    current_file_path = __file__
    for index, frame in enumerate(frames):
        if current_file_path == frame.filename:
            break

    try:
        frame_of_file_doing_importing = frames[index + 1]
    except IndexError:
        raise IndexError("The next frame which represents the importing file doesn't exist")

    path = frame_of_file_doing_importing.filename
    return path


def get_absolute_directory_path_of_file_doing_importing(frames):
    path = get_absolute_path_of_file_doing_importing(frames)
    return os.path.dirname(path)


def define_path_relative_to_file_doing_importing(resource, frames):
    path_to_directory_of_file_doing_importing = get_absolute_directory_path_of_file_doing_importing(frames)
    relative_path_of_resource = os.path.join(path_to_directory_of_file_doing_importing, resource)
    absolute_path_of_resource = os.path.abspath(relative_path_of_resource)
    return absolute_path_of_resource


def define_path_based_on_resource_directory(resource, absolute_path_to_resource_directory):
    absolute_path_of_resource = os.path.join(absolute_path_to_resource_directory, resource)
    return absolute_path_of_resource


def define_init_file_in_python_package(absolute_file_path_of_target_resource):
    return os.path.join(absolute_file_path_of_target_resource, '__init__.py')


def get_file_extension(absolute_path_of_resource):
    _, file_extension = os.path.splitext(absolute_path_of_resource)
    return file_extension


def is_python_package(absolute_path_of_resource):
    file_extension = get_file_extension(absolute_path_of_resource)
    return file_extension == ''


def modify_resource_path_for_packages(absolute_path_of_target_resource):
    if is_python_package(absolute_path_of_target_resource):
        absolute_path_of_target_resource = define_init_file_in_python_package(absolute_path_of_target_resource)
    return absolute_path_of_target_resource


def get_resource_spec(absolute_path_of_resource):
    spec = importlib.util.spec_from_file_location('', absolute_path_of_resource)
    if spec is None:
        raise ImportError('Resource does not exist.')
    return spec


def module_is_already_loaded(absolute_path_of_resource):
    return absolute_path_of_resource in sys.modules


def add_module_to_global_modules(absolute_path_of_resource, resource_module):
    sys.modules[absolute_path_of_resource] = resource_module


def load_resource_module(resource_module, spec):
    spec.loader.exec_module(resource_module)


def import_file(resource, absolute_path_to_resource_directory=None):

    if absolute_path_to_resource_directory is None:
        frames = inspect.stack()
        absolute_path_of_resource = define_path_relative_to_file_doing_importing(resource, frames)
    else:
        absolute_path_of_resource = define_path_based_on_resource_directory(
            resource,
            absolute_path_to_resource_directory
        )

    absolute_path_of_resource = modify_resource_path_for_packages(absolute_path_of_resource)
    spec = get_resource_spec(absolute_path_of_resource)
    resource_module = importlib.util.module_from_spec(spec)

    if module_is_already_loaded(absolute_path_of_resource):
        return sys.modules[absolute_path_of_resource]

    load_resource_module(resource_module, spec)
    add_module_to_global_modules(absolute_path_of_resource, resource_module)
    return resource_module

