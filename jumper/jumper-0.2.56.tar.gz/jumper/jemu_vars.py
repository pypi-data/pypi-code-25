import sys, os

CORE_LINUX_OS = "linux"
CORE_WINDOWS_OS1 = "win"
CORE_WINDOWS_OS2 = "cygwin"
CORE_MAC_OS = "darwin"

JEMU_LINUX_DIR = "jemu-linux"
JEMU_MAC_DIR = "jemu-mac"
JEMU_WINDOWS_DIR = "jemu-windows"

HERE = os.path.abspath(os.path.dirname(__file__))


def get_jemu_path():
    jemu_dest = None
    if sys.platform.startswith(CORE_LINUX_OS):
        jemu_dest = os.path.join(HERE, 'jemu', JEMU_LINUX_DIR, 'jemu')
    elif sys.platform.startswith(CORE_MAC_OS):
        jemu_dest = os.path.join(HERE, 'jemu', JEMU_MAC_DIR, 'jemu')
    elif sys.platform.startswith(CORE_WINDOWS_OS1) or sys.platform.startswith(CORE_WINDOWS_OS2):
        jemu_dest = os.path.join(HERE, 'jemu', JEMU_WINDOWS_DIR, 'jemu.exe')
    return jemu_dest
