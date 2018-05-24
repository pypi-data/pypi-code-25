import os
import shutil
from builtins import input
from .task import Task
# from task import Task


progress_enabled = True
pbar = None
try:
    from progressbar import ProgressBar
except Exception as e:
    progress_enabled = False
    print('Library `progressbar2` not found. Not printing progress bars for this session.')


class InstallTools(Task):
    """Helper to perform miscellaneous installation tasks."""

    def __init__(self, debug=False):
        super(InstallTools, self).__init__(debug)
        self.progress_enabled = progress_enabled

    def show_progress(self, block_num, block_size, total_size):
        global pbar
        if not progress_enabled:
            return
        if pbar is None:
            pbar = ProgressBar(maxval=total_size)

        downloaded = block_num * block_size
        if downloaded < total_size:
            pbar.update(downloaded)
        else:
            pbar.finish()
            pbar = None

    def move_files(self):
        if os.path.isdir('nwjs-v0.24.3-osx-x64/nwjs.app/Contents/Resources/app.nw'):
            print('App destination exists. Overwriting...')
            shutil.rmtree(
                'nwjs-v0.24.3-osx-x64/nwjs.app/Contents/Resources/app.nw', ignore_errors=True)

        shutil.copytree('./tokyo_dark/package.nw',
                        './nwjs-v0.24.3-osx-x64/nwjs.app/Contents/Resources/app.nw')

    def move_icons(self):
        dest1 = 'nwjs-v0.24.3-osx-x64/nwjs.app/Contents/Resources/app.icns'
        dest2 = 'nwjs-v0.24.3-osx-x64/nwjs.app/Contents/Resources/document.icns'
        if os.path.isfile(dest1):
            os.remove(dest1)

        if os.path.isfile(dest2):
            os.remove(dest2)

        shutil.copy2('logo.icns', dest1)
        shutil.copy2('logo.icns', dest2)

    def move_app(self, dest):
        while os.path.isdir(dest + '/Tokyo Dark.app'):
            rst = input('Destination already exists. Overwrite? (y/n): ')
            if rst == 'y':
                shutil.rmtree(dest + '/Tokyo Dark.app', ignore_errors=True)
            else:
                dest = input(
                    'Where do you want to store Tokyo Dark.app? (e.g. /Applications): ')

        print('Installing application...')
        if (os.path.isdir('nwjs-v0.24.3-osx-x64/nwjs.app') and not
                os.path.isdir('nwjs-v0.24.3-osx-x64/Tokyo Dark.app')):
            shutil.move('nwjs-v0.24.3-osx-x64/nwjs.app',
                        'nwjs-v0.24.3-osx-x64/Tokyo Dark.app')

        shutil.copytree('nwjs-v0.24.3-osx-x64/Tokyo Dark.app',
                        dest + '/Tokyo Dark.app', symlinks=True)


if __name__ == '__main__':
    test = InstallTools()
    test.move_app('/Applications')
