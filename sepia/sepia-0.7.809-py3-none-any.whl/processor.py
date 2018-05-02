#!/usr/bin/python3


class IncludeHelper(object):
    def __init__(self, base_path):
        self.base_path = base_path

    def _get_file_path(self, *path_parts):
        from os.path import abspath
        from os.path import expanduser
        from os.path import expandvars
        from os.path import isfile
        from os.path import join
        from os.path import normpath

        if len(path_parts):
            if type(path_parts[0]) is str:
                return abspath(normpath(expandvars(expanduser(join(self.base_path, *path_parts)))))

            for path_parts_try in path_parts:
                path_try = abspath(normpath(expandvars(expanduser(join(self.base_path, *path_parts_try)))))

                if isfile(path_try):
                    return path_try

                print('"\033[33m{0}\033[0m" was not found.'.format(path_try))

        return self.base_path

    def include_plain(self, *path_parts):
        with open(self._get_file_path(*path_parts), 'r') as file:
            return file.read()

    def include_markdown(self, *path_parts):
        from markdown import markdown

        with open(self._get_file_path(*path_parts), 'r') as file:
            return markdown(
                file.read(),
                extensions=[
                    'markdown.extensions.abbr',
                    'markdown.extensions.attr_list',
                    'markdown.extensions.def_list',
                    'markdown.extensions.footnotes',
                    'markdown.extensions.tables',
                    'markdown.extensions.smart_strong',
                ])


def include_stdout(*path_parts):
    from subprocess import PIPE
    from subprocess import run

    return run(*path_parts, stdout=PIPE).stdout


class Processor(object):
    def __init__(self, template_set, variable_set, output_path):
        self._template_set = template_set
        self._variable_set = variable_set
        self._output_path = output_path

    def execute(self):
        from jinja2 import FileSystemLoader
        from jinja2.sandbox import SandboxedEnvironment
        from os import makedirs
        from os.path import dirname
        from os.path import join
        from shutil import copy2
        from shutil import copystat

        for destination_name, source_info in self._template_set.constant.items():
            destination_path = join(self._output_path, destination_name)
            destination_dir = dirname(destination_path)
            makedirs(destination_dir, exist_ok=True)

            copy2(source_info.file_path, destination_path)

        for destination_name, source_info in self._template_set.variable.items():
            destination_path = join(self._output_path, destination_name)
            destination_dir = dirname(destination_path)
            makedirs(destination_dir, exist_ok=True)

            loader = FileSystemLoader(source_info.base_path)
            include_helper = IncludeHelper(source_info.base_path)
            environment = SandboxedEnvironment(
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=False,
                autoescape=False,
                loader=loader)
            environment.globals.update(self._variable_set.data)
            environment.globals['include_plain'] = include_helper.include_plain
            environment.globals['include_markdown'] = include_helper.include_markdown
            environment.globals['include_stdout'] = include_stdout
            template_context = {}

            with open(source_info.file_path, 'r') as source_file:
                source_text = source_file.read()

            template = environment.from_string(source_text)
            destination_text = template.render(template_context)

            with open(destination_path, 'w') as destination_file:
                destination_file.write(destination_text)

            copystat(source_info.file_path, destination_path)
