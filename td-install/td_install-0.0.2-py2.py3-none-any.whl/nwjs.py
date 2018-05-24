import os
import subprocess
import shutil
from .task import Task

try:
    import urllib.request as urllib
except Exception as e:
    import urllib


class NWjs(Task):
    """docstring for NWjs"""

    def __init__(self, progress_hook, debug=False):
        super(NWjs, self).__init__(debug)
        self.progress_hook = progress_hook
        self.folders = [
            'nwjs-v0.24.3-osx-x64'
        ]

        self.files = [
            'nwjs-v0.24.3-osx-x64.zip'
        ]
        self.sdk = False
        self.clean()

    def download_nwjs(self, sdk=False):
        self.sdk = sdk
        url = 'https://dl.nwjs.io/v0.24.3/nwjs-v0.24.3-osx-x64.zip'
        if sdk:
            url = 'https://dl.nwjs.io/v0.24.3/nwjs-sdk-v0.24.3-osx-x64.zip'
            print('Downloading nwjs (sdk)...')
        else:
            print('Downloading nwjs...')
        urllib.urlretrieve(url, 'nwjs-v0.24.3-osx-x64.zip',
                           reporthook=self.progress_hook)

    def extract_nwjs(self):
        print('Extracting nwjs...')
        FNULL = open(os.devnull, 'w')
        try:
            subprocess.check_call(['unzip', '-q', 'nwjs-v0.24.3-osx-x64.zip'],
                                  stdout=self.stdout, stderr=self.stderr)
        except Exception as e:
            print('Extraction of nwjs-v0.24.3-osx-x64.zip using unzip command failed.')
            print(e)
            exit(1)

        if self.sdk:
            shutil.move('nwjs-sdk-v0.24.3-osx-x64', 'nwjs-v0.24.3-osx-x64')
