#!/usr/bin/env python3
"""
simple dunder documentation generator
"""
import os


def get_module_doc(filepath):
    """Get module-level __doc__ of python module at filepath"""
    doc = 'no documentation found'
    module = compile(open(filepath).read(), filepath, 'exec')
    if module.co_consts:
        potential_doc = module.co_consts[0]
        if isinstance(potential_doc, str) and module.co_names[0] == '__doc__':
            if potential_doc[0] == '\n':
                potential_doc = potential_doc[1:]
            if potential_doc[-1] == '\n':
                potential_doc = potential_doc[:-1]
            doc = potential_doc.replace('\n', ' ')
    return doc


def list_files(start_path='', extension='.py', indent=2, pad=22):
    """main file tree generator"""
    if not start_path:
        start_path = os.getcwd()
    full_tree = ''
    for root, dirs, files in os.walk(start_path):
        dirs.sort()
        level = root.replace(start_path, '').count(os.sep)
        indent_string = ' ' * indent * (level)
        directory = '{}{}/\n'.format(indent_string, os.path.basename(root))
        files_tree = ''
        subindent = ' ' * indent * (level + 1)
        files = [x for x in sorted(files) if x.endswith(extension)]
        for f in files:
            filename = '{}:'.format(f).ljust(pad)
            full_path = os.path.join(root, f)
            if '/env/' in full_path:
                continue
            doc = get_module_doc(full_path)
            files_tree += '{}{}{}\n'.format(subindent, filename, doc)
        if files_tree:
            full_tree += directory
            full_tree += files_tree
            full_tree += '\n'
    return full_tree


if __name__ == '__main__':
    print(list_files())
