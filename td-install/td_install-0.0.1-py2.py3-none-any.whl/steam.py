import subprocess
import tarfile
import patch
from builtins import input
from pkg_resources import resource_filename
from getpass import getpass
from .task import Task

try:
    import urllib.request as urllib
except Exception as e:
    import urllib


class SteamCMD(Task):
    """docstring for SteamCMD"""

    def __init__(self, progress_hook, debug=False):
        super(SteamCMD, self).__init__(debug)
        self.folders = [
            'frameworks',
            'osx32',
            'package',
            'public',
            'tokyo_dark',
        ]

        self.files = [
            'steamcmd',
            'steamcmd.sh',
            'steamcmd_osx.tar.gz',
            'crashhandler.dylib',
            'libaudio.dylib',
            'libsteaminput.dylib',
            'libtier0_s.dylib',
            'libvstdlib_s.dylib',
            'steamclient.dylib',
            'steamconsole.dylib',
        ]
        self.progress_hook = progress_hook
        self.clean()

    def download_steam(self):
        print('Downloading SteamCMD...')
        urllib.urlretrieve(
            'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_osx.tar.gz',
            'steamcmd_osx.tar.gz',
            reporthook=self.progress_hook)

        print('Extracting SteamCMD...')
        tar = tarfile.open('steamcmd_osx.tar.gz')
        tar.extractall()
        tar.close()

    def download_game(self):
        print('Downloading Tokyo Dark from Steam...')
        print('You must log into Steam first. Your credentials are sent directly to Valve through SteamCMD.')
        user = input('Please enter username: ')
        password = getpass('Please enter password: ')
        print('Downloading... This may take a while...')
        print('Note: Steam will likely open a Finder window. You may close this window.')
        print(("Note II: Steam may randomly hang or crash after logging in or "
               "updating. Crashing is obvious, however, if you think Steam is "
               "hanging, you can check Activity Monitor to see if there is "
               "signifigant network activity (which would indicate it has not "
               "gotten stuck)."))
        try:
            subprocess.check_call([
                './steamcmd.sh', '+@sSteamCmdForcePlatformType windows ',
                '+login ' + user + ' ' + password,
                '+force_install_dir ./tokyo_dark',
                '+app_update 687260 validate', '+quit'], stdout=self.stdout, stderr=self.stderr)
        except Exception as e:
            print('SteamCMD command failed.')
            # print(e)
            exit(1)

    def download_api(self):
        print('Downloading Steam API for macOS...')
        urllib.urlretrieve(
            'https://github.com/Facepunch/Facepunch.Steamworks.Unity/raw/master/libsteam_api.dylib',
            'nwjs-v0.24.3-osx-x64/nwjs.app/Contents/Resources/app.nw/libsteam_api.dylib',
            reporthook=self.progress_hook)

    def patch_load(self):
        print('Patching small bug...')
        pset = patch.fromfile(resource_filename(__name__, 'test.patch'))
        pset.apply()


if __name__ == '__main__':
    test = SteamCMD(None, True)
    test.patch_load()
