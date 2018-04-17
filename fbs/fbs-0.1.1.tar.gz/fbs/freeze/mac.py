from fbs import path, SETTINGS
from fbs.freeze import run_pyinstaller
from fbs.resources import generate_resources, get_icons
from os import makedirs, unlink, rename, symlink
from os.path import exists
from shutil import copy, rmtree
from subprocess import run

def freeze_mac():
    if not exists(path('target/Icon.icns')):
        _generate_iconset()
        run(['iconutil', '-c', 'icns', path('target/Icon.iconset')], check=True)
    pyinstaller_args = [
        '--windowed',
        '--icon', path('target/Icon.icns')
    ]
    bundle_identifier = SETTINGS.get('mac_bundle_identifier', '')
    if bundle_identifier:
        pyinstaller_args.extend([
            '--osx-bundle-identifier', bundle_identifier
        ])
    run_pyinstaller(extra_args=pyinstaller_args)
    _remove_unwanted_pyinstaller_files()
    _fix_sparkle_delta_updates()
    generate_resources(
        dest_dir=path('${freeze_dir}'),
        dest_dir_for_base=path('${freeze_dir}/Contents/Resources')
    )

def _generate_iconset():
    makedirs(path('target/Icon.iconset'), exist_ok=True)
    for size, icon_path in get_icons():
        dest_name = 'icon_%dx%d.png' % (size, size)
        copy(icon_path, path('target/Icon.iconset/' + dest_name))

def _remove_unwanted_pyinstaller_files():
    for unwanted in ('include', 'lib', 'lib2to3'):
        try:
            unlink(path('${freeze_dir}/Contents/MacOS/' + unwanted))
        except FileNotFoundError:
            pass
        try:
            rmtree(path('${freeze_dir}/Contents/Resources/' + unwanted))
        except FileNotFoundError:
            pass

def _fix_sparkle_delta_updates():
    # Sparkle's Delta Updates mechanism does not support signed non-Mach-O files
    # in Contents/MacOS. base_library.zip, which is created by PyInstaller,
    # violates this. We therefore move base_library.zip to Contents/Resources.
    # Fortunately, everything still works if we then create a symlink
    # MacOS/base_library.zip -> ../Resources/base_library.zip.
    rename(
        path('${freeze_dir}/Contents/MacOS/base_library.zip'),
        path('${freeze_dir}/Contents/Resources/base_library.zip')
    )
    symlink(
        '../Resources/base_library.zip',
        path('${freeze_dir}/Contents/MacOS/base_library.zip')
    )