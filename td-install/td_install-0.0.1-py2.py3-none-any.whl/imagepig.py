import os
import subprocess
from glob import glob
import shutil
# from task import Task
from .task import Task

try:
    import urllib.request as urllib
except Exception as e:
    import urllib


class ImagePig(Task):
    """docstring for ImagePig"""

    def __init__(self, progress_hook, debug=False):
        super(ImagePig, self).__init__(debug)
        self.progress_hook = progress_hook
        self.folders = [
            'logo',
            'logo.iconset'
        ]

        self.files = [
            'logo.zip',
            'logo.icns'
        ]
        self.clean()

    def start(self):
        self.dl_icons()
        self.gen_icons()

    def dl_icons(self):
        url = 'http://www.tokyodark.com/presskit/Tokyo_Dark/images/logo.zip'
        print('Downloading logo...')
        urllib.urlretrieve(url, 'logo.zip',
                           reporthook=self.progress_hook)

        print('Extracting logo...')
        try:
            subprocess.check_call(['unzip', '-q', 'logo.zip', '-d', './logo'],
                                  stdout=self.stdout, stderr=self.stderr)
        except Exception as e:
            print('Extraction of logo.zip using unzip command failed.')
            print(e)
            exit(1)

    def gen_icons(self):
        print('Generating icons...')
        sizes = ['16', '32', '128', '256', '512']
        old_cwd = os.getcwd()
        os.chdir(old_cwd + '/logo')
        # convert logo to pngs of different sizes
        for size in sizes:
            try:
                icon = 'icon_' + size + 'x' + size
                icon2x = 'icon_' + size + 'x' + size + '@2'
                subprocess.check_call(
                    ['sips', '-Z', size, 'LOGO-large-trim.jpg', '--padToHeightWidth',
                        size, size, '--out', icon + '.jpg'],
                    stdout=self.stdout, stderr=self.stderr)
                subprocess.check_call(
                    ['sips', '-Z', str(int(size) * 2), 'LOGO-large-trim.jpg', '--padToHeightWidth',
                        str(int(size) * 2), str(int(size) * 2), '--out', icon2x + '.jpg'],
                    stdout=self.stdout, stderr=self.stderr)

                subprocess.check_call(
                    ['sips', '-s', 'format', 'png', icon + '.jpg', '--out', icon + '.png'],
                    stdout=self.stdout, stderr=self.stderr)
                subprocess.check_call(
                    ['sips', '-s', 'format', 'png', icon2x + '.jpg', '--out', icon2x + '.png'],
                    stdout=self.stdout, stderr=self.stderr)
            except Exception as e:
                print('Logo generation failed.')
                print(e)
                exit(1)

        filelist = glob('*.jpg')
        for file in filelist:
            os.remove(file)
        os.remove('blacklogo.png')

        # convert folder to icns
        os.chdir(old_cwd)
        shutil.move('logo', 'logo.iconset')
        try:
            subprocess.check_call(['iconutil', '-c', 'icns', 'logo.iconset'],
                                  stdout=self.stdout, stderr=self.stderr)
        except Exception as e:
            print('Iconset command failed.')
            print(e)
            exit(1)

if __name__ == '__main__':
    test = ImagePig(None, True)
    test.dl_icons()
    test.gen_icons()
