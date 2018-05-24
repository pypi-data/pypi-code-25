import inspect
import os
import re
from types import ModuleType


class ModuleLoader:
    @staticmethod
    def folder_to_module(name, directory_name):
        main_module = ModuleType(name)
        directory = os.fsencode(directory_name)

        for file in os.listdir(directory):
            ModuleLoader._file_to_module(
                file.decode('ascii'),
                main_module,
                directory.decode('ascii'))

        return main_module

    @staticmethod
    def objects_from_module(suffix, main_module):
        for name, data in inspect.getmembers(main_module, inspect.ismodule):
            for _, move in inspect.getmembers(data, inspect.isclass):
                yield re.sub(suffix, '', name), move()

    @staticmethod
    def _file_to_module(filename, main, directory):
        if filename.endswith(".py"):
            submodule_name = re.sub('\.py', '', filename)
            setattr(main, submodule_name, ModuleType(submodule_name))

            ModuleLoader._compile_file(directory + '/' + filename, main, submodule_name)

    @staticmethod
    def _compile_file(filename, main, submodule):
        with open(filename) as content:
            exec(content.read(), getattr(main, submodule).__dict__)
