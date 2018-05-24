from .install import InstallTools
from .steam import SteamCMD
from .nwjs import NWjs
from .imagepig import ImagePig
from builtins import input
import atexit


def main(debug=False):
    helper = InstallTools(debug)
    steam = SteamCMD(helper.show_progress, debug)
    nwjs = NWjs(helper.show_progress, debug)
    pig = ImagePig(helper.show_progress, debug)

    steam.download_steam()
    steam.download_game()

    nwjs.download_nwjs(debug)
    nwjs.extract_nwjs()

    helper.move_files()

    pig.dl_icons()
    pig.gen_icons()

    helper.move_icons()

    steam.patch_load()
    steam.steam_id()
    steam.download_api()

    print('Done.')
    dest = input(
        'Where do you want to store Tokyo Dark.app? (e.g. /Applications): ')
    helper.move_app(dest)

    print('All set! You can now find the application at the location you specified.')
    resp = input('Cleanup build directory? (y/n): ')
    if resp == 'y':
        cleanup(pig, nwjs, steam)


def debug():
    main(True)


def cleanup(images, js, steam):
    images.clean()
    js.clean()
    steam.clean()


if __name__ == '__main__':
    main()
