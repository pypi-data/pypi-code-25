import os
import shutil

WORKING_DIRECTORY = '/tmp/TD_INSTALL'


class Task(object):
    """docstring for Task"""

    def __init__(self, debug=False):
        if not os.path.exists(WORKING_DIRECTORY):
            os.makedirs(WORKING_DIRECTORY)

        os.chdir(WORKING_DIRECTORY)
        self.files = []
        self.folder = []
        FNULL = open(os.devnull, 'w')
        self.stdout = FNULL
        self.stderr = FNULL

        if debug:
            self.stdout = None
            self.stderr = None

    def clean(self):
        for file in self.files:
            if os.path.isfile(file):
                os.remove(file)

        for folder in self.folders:
            if os.path.isdir(folder):
                shutil.rmtree(folder, ignore_errors=True)
