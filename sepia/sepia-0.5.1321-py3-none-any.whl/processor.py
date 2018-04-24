#!/usr/bin/python3


class IncludeHelper(object):
    def __init__(self, base_path):
        self.base_path = base_path

    def _read_file_text(self, *path_paths):
        from os.path import abspath
        from os.path import expanduser
        from os.path import expandvars
        from os.path import join
        from os.path import normpath

        file_path = abspath(normpath(expandvars(expanduser(join(self.base_path, *path_paths)))))

        with open(file_path, 'r') as file:
            return file.read()

    def include_plain(self, *path_paths):
        return self._read_file_text(*path_paths)

    def include_markdown(self, *path_paths):
        from markdown import markdown

        text = self._read_file_text(*path_paths)

        return markdown(text)


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
            template_context = {}

            with open(source_info.file_path, 'r') as source_file:
                source_text = source_file.read()

            template = environment.from_string(source_text)
            destination_text = template.render(template_context)

            with open(destination_path, 'w') as destination_file:
                destination_file.write(destination_text)

            copystat(source_info.file_path, destination_path)
