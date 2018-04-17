import pathlib
import platform

import pkg_resources

BASE_PATH = pathlib.Path("bin")
EXE_NAME_TMPL = "nucamino-{os}-{arch}{ext}"
EXTENSIONS = {
    "windows": ".exe",
}


def path():
    '''Returns the path the nucamino binary.

    This function returns the path the the operating-system and
    processor appropriate nucamino binary embedded in this package.

    Assuming that the python process that loads the module is only
    running on one computer, it should be fine to retrieve this path
    while modules are being loaded.
    '''
    os = platform.system().lower()
    arch_name, _ = platform.architecture()
    if '32' in arch_name:
        arch = '386'
    else:
        arch = 'amd64'
    ext = EXTENSIONS.get(os, "")
    exe_name = EXE_NAME_TMPL.format(
        os=os,
        arch=arch,
        ext=ext,
    )
    resource_path = BASE_PATH / exe_name
    return pkg_resources.resource_filename(
        "pynucamino",
        str(resource_path),
    )
