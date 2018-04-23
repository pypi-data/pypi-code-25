import os


def get_content_directories(root_directory):

    def is_content_directory(d):
        ignored_directories = ['assets', 'translations']
        return os.path.isdir(os.path.join(root_directory, d)) and d not in ignored_directories and not d.startswith('.')

    return filter(is_content_directory, os.listdir(root_directory))


class WorkingDirectory(object):
    """ Context manager for changing directory"""
    def __init__(self, new_dir):
        self.new_dir = new_dir
        self.old_dir = None

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.new_dir)

    def __exit__(self, *_):
        os.chdir(self.old_dir)
