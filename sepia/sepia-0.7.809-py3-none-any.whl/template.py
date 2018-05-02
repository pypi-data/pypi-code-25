#!/usr/bin/python3


class TemplateSourceInfo(object):
    def __init__(self, base_path, file_path):
        self.base_path = base_path
        self.file_path = file_path


class TemplateSet(object):
    def __init__(self):
        self.variable = {}
        self.constant = {}

    def _add_file(self, source_dir, source_path, destination_path):
        if '/.' not in source_path:
            if destination_path.endswith('.~'):
                self.variable[destination_path[:-2]] = TemplateSourceInfo(source_dir, source_path)
            else:
                self.constant[destination_path] = TemplateSourceInfo(source_dir, source_path)

    def add_path(self, path):
        from os import walk
        from os.path import basename
        from os.path import isdir
        from os.path import isfile
        from os.path import join

        if isdir(path):
            for root, _, files in walk(path):
                for file in files:
                    full_path = join(root, file)
                    self._add_file(path, full_path, full_path[len(path) + 1:])
        elif isfile(path):
            self._add_file(basename(path), path, basename(path))

