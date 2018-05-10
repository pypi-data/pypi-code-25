"""Pyperclip

A cross-platform clipboard module for Python, with copy & paste functions for plain text.
By Al Sweigart al@inventwithpython.com.
Modified version by bindh3x <os@bindh3x.io> added clear function, and dropped
 Windows support.

BSD License

Usage:
  import pyperclip
  pyperclip.copy('The text to be copied to the clipboard.')
  spam = pyperclip.paste()
  pyperclip.clear()

  if not pyperclip.is_available():
    print("Copy functionality unavailable!")

On Windows, no additional modules are needed.
On Mac, the pyobjc module is used, falling back to the pbcopy and pbpaste cli
    commands. (These commands should come with OS X.).
On Linux, install xclip or xsel via package manager. For example, in Debian:
    sudo apt-get install xclip
    sudo apt-get install xsel

Otherwise on Linux, you will need the gtk or PyQt5/PyQt4 modules installed.

gtk and PyQt4 modules are not available for Python 3,
and this module does not work with PyGObject yet.

Note: There seem sto be a way to get gtk on Python 3, according to:
    https://askubuntu.com/questions/697397/python3-is-not-supporting-gtk-module

Security Note: This module runs programs with these names:
    - which
    - where
    - pbcopy
    - pbpaste
    - xclip
    - xsel
    - klipper
    - qdbus
A malicious user could rename or add programs with these names, tricking
Pyperclip into running them with whatever permissions the Python process has.

"""
__version__ = '1.6.0'

import ctypes
import os
import platform
import subprocess
import sys
import time
import warnings

from ctypes import c_size_t, sizeof, c_wchar_p, get_errno, c_wchar


# `import PyQt4` sys.exit()s if DISPLAY is not in the environment.
# Thus, we need to detect the presence of $DISPLAY manually
# and not load PyQt4 if it is absent.
HAS_DISPLAY = os.getenv("DISPLAY", False)

EXCEPT_MSG = """
    Pyperclip could not find a copy/paste mechanism for your system.
    For more information, please visit https://pyperclip.readthedocs.io/en/latest/introduction.html#not-implemented-error """

PY2 = sys.version_info[0] == 2

STR_OR_UNICODE = unicode if PY2 else str

ENCODING = 'utf-8'
WHICH = "which"

def _executable_exists(name):
    return subprocess.call([WHICH, name],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0



# Exceptions
class PyperclipException(RuntimeError):
    pass

class PyperclipWindowsException(PyperclipException):
    def __init__(self, message):
        message += " (%s)" % ctypes.WinError()
        super(PyperclipWindowsException, self).__init__(message)



def init_osx_pbcopy_clipboard():

    def copy_osx_pbcopy(text):
        p = subprocess.Popen(['pbcopy', 'w'],
                             stdin=subprocess.PIPE, close_fds=True)
        p.communicate(input=text.encode(ENCODING))

    def paste_osx_pbcopy():
        p = subprocess.Popen(['pbpaste', 'r'],
                             stdout=subprocess.PIPE, close_fds=True)
        stdout, stderr = p.communicate()
        return stdout.decode(ENCODING)

    def clear_osx_pbcopy():
        return None

    return copy_osx_pbcopy, paste_osx_pbcopy, clear_osx_pbcopy


def init_osx_pyobjc_clipboard():
    def copy_osx_pyobjc(text):
        '''Copy string argument to clipboard'''
        newStr = Foundation.NSString.stringWithString_(text).nsstring()
        newData = newStr.dataUsingEncoding_(Foundation.NSUTF8StringEncoding)
        board = AppKit.NSPasteboard.generalPasteboard()
        board.declareTypes_owner_([AppKit.NSStringPboardType], None)
        board.setData_forType_(newData, AppKit.NSStringPboardType)

    def paste_osx_pyobjc():
        "Returns contents of clipboard"
        board = AppKit.NSPasteboard.generalPasteboard()
        content = board.stringForType_(AppKit.NSStringPboardType)
        return content

    def clear_osx_pyobjc():
        return None

    return copy_osx_pyobjc, paste_osx_pyobjc, clear_osx_pyobjc


def init_gtk_clipboard():
    global gtk
    import gtk

    def copy_gtk(text):
        global cb
        cb = gtk.Clipboard()
        cb.set_text(text)
        cb.store()

    def paste_gtk():
        clipboardContents = gtk.Clipboard().wait_for_text()
        # for python 2, returns None if the clipboard is blank.
        if clipboardContents is None:
            return ''
        else:
            return clipboardContents

    def clear_gtk():
        return None

    return copy_gtk, paste_gtk, clear_gtk


def init_qt_clipboard():
    global QApplication
    # $DISPLAY should exist

    # Try to import from qtpy, but if that fails try PyQt5 then PyQt4
    try:
        from qtpy.QtWidgets import QApplication
    except:
        try:
            from PyQt5.QtWidgets import QApplication
        except:
            from PyQt4.QtGui import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    def copy_qt(text):
        cb = app.clipboard()
        cb.setText(text)

    def paste_qt():
        cb = app.clipboard()
        return STR_OR_UNICODE(cb.text())

    def clear_qt():
        return None

    return copy_qt, paste_qt, clear_qt


def init_xclip_clipboard():
    DEFAULT_SELECTION='c'
    PRIMARY_SELECTION='p'

    def copy_xclip(text, primary=False):
        selection=DEFAULT_SELECTION
        if primary:
            selection=PRIMARY_SELECTION
        p = subprocess.Popen(['xclip', '-selection', selection],
                             stdin=subprocess.PIPE, close_fds=True)
        p.communicate(input=text.encode(ENCODING))

    def paste_xclip(primary=False):
        selection=DEFAULT_SELECTION
        if primary:
            selection=PRIMARY_SELECTION
        p = subprocess.Popen(['xclip', '-selection', selection, '-o'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True)
        stdout, stderr = p.communicate()
        # Intentionally ignore extraneous output on stderr when clipboard is empty
        return stdout.decode(ENCODING)

    def clear_xclip():
        return None

    return copy_xclip, paste_xclip, clear_xclip


def init_xsel_clipboard():
    DEFAULT_SELECTION='-b'
    PRIMARY_SELECTION='-p'

    def copy_xsel(text, primary=False):
        selection_flag = DEFAULT_SELECTION
        if primary:
            selection_flag = PRIMARY_SELECTION
        p = subprocess.Popen(['xsel', selection_flag, '-i'],
                             stdin=subprocess.PIPE, close_fds=True)
        p.communicate(input=text.encode(ENCODING))

    def paste_xsel(primary=False):
        selection_flag = DEFAULT_SELECTION
        if primary:
            selection_flag = PRIMARY_SELECTION
        p = subprocess.Popen(['xsel', selection_flag, '-o'],
                             stdout=subprocess.PIPE, close_fds=True)
        stdout, stderr = p.communicate()
        return stdout.decode(ENCODING)

    def clear_xsel(primary=False):
        selection_flag = DEFAULT_SELECTION
        if primary:
            selection_flag = PRIMARY_SELECTION
        p = subprocess.Popen(['xsel', selection_flag, '-c'],
                             stdout=subprocess.PIPE, close_fds=True)
        # stdout, stderr = p.communicate()
        return True

    return copy_xsel, paste_xsel, clear_xsel


def init_klipper_clipboard():
    def copy_klipper(text):
        p = subprocess.Popen(
            ['qdbus', 'org.kde.klipper', '/klipper', 'setClipboardContents',
             text.encode(ENCODING)],
            stdin=subprocess.PIPE, close_fds=True)
        p.communicate(input=None)

    def paste_klipper():
        p = subprocess.Popen(
            ['qdbus', 'org.kde.klipper', '/klipper', 'getClipboardContents'],
            stdout=subprocess.PIPE, close_fds=True)
        stdout, stderr = p.communicate()

        # Workaround for https://bugs.kde.org/show_bug.cgi?id=342874
        # TODO: https://github.com/asweigart/pyperclip/issues/43
        clipboardContents = stdout.decode(ENCODING)
        # even if blank, Klipper will append a newline at the end
        assert len(clipboardContents) > 0
        # make sure that newline is there
        assert clipboardContents.endswith('\n')
        if clipboardContents.endswith('\n'):
            clipboardContents = clipboardContents[:-1]
        return clipboardContents

    def clear_klipper():
        return None

    return copy_klipper, paste_klipper, clear_klipper


def init_no_clipboard():
    class ClipboardUnavailable(object):

        def __call__(self, *args, **kwargs):
            raise PyperclipException(EXCEPT_MSG)

        if PY2:
            def __nonzero__(self):
                return False
        else:
            def __bool__(self):
                return False

    return ClipboardUnavailable(), ClipboardUnavailable()

# Automatic detection of clipboard mechanisms and importing is done in deteremine_clipboard():
def determine_clipboard():
    '''
    Determine the OS/platform and set the copy() and paste() functions
    accordingly.
    '''

    global Foundation, AppKit, gtk, qtpy, PyQt4, PyQt5

    # Setup for the MAC OS X platform:
    if os.name == 'mac' or platform.system() == 'Darwin':
        try:
            import Foundation  # check if pyobjc is installed
            import AppKit
        except ImportError:
            return init_osx_pbcopy_clipboard()
        else:
            return init_osx_pyobjc_clipboard()

    # Setup for the LINUX platform:
    if HAS_DISPLAY:
        try:
            import gtk  # check if gtk is installed
        except ImportError:
            pass # We want to fail fast for all non-ImportError exceptions.
        else:
            return init_gtk_clipboard()

        if _executable_exists("xclip"):
            return init_xclip_clipboard()
        if _executable_exists("xsel"):
            return init_xsel_clipboard()
        if _executable_exists("klipper") and _executable_exists("qdbus"):
            return init_klipper_clipboard()

        try:
            # qtpy is a small abstraction layer that lets you write applications using a single api call to either PyQt or PySide.
            # https://pypi.python.org/pypi/QtPy
            import qtpy  # check if qtpy is installed
        except ImportError:
            # If qtpy isn't installed, fall back on importing PyQt4.
            try:
                import PyQt5  # check if PyQt5 is installed
            except ImportError:
                try:
                    import PyQt4  # check if PyQt4 is installed
                except ImportError:
                    pass # We want to fail fast for all non-ImportError exceptions.
                else:
                    return init_qt_clipboard()
            else:
                return init_qt_clipboard()
        else:
            return init_qt_clipboard()


    return init_no_clipboard()


def set_clipboard(clipboard):
    '''
    Explicitly sets the clipboard mechanism. The "clipboard mechanism" is how
    the copy() and paste() functions interact with the operating system to
    implement the copy/paste feature. The clipboard parameter must be one of:
        - pbcopy
        - pbobjc (default on Mac OS X)
        - gtk
        - qt
        - xclip
        - xsel
        - klipper
        - windows (default on Windows)
        - no (this is what is set when no clipboard mechanism can be found)
    '''
    global copy, paste, clear

    clipboard_types = {'pbcopy': init_osx_pbcopy_clipboard,
                       'pyobjc': init_osx_pyobjc_clipboard,
                       'gtk': init_gtk_clipboard,
                       'qt': init_qt_clipboard, # TODO - split this into 'qtpy', 'pyqt4', and 'pyqt5'
                       'xclip': init_xclip_clipboard,
                       'xsel': init_xsel_clipboard,
                       'klipper': init_klipper_clipboard,
                       'no': init_no_clipboard}

    if clipboard not in clipboard_types:
        raise ValueError('Argument must be one of %s' % (', '.join([repr(_) for _ in clipboard_types.keys()])))

    # Sets pyperclip's copy() and paste() functions:
    copy, paste, clear = clipboard_types[clipboard]()


def lazy_load_stub_copy(text):
    '''
    A stub function for copy(), which will load the real copy() function when
    called so that the real copy() function is used for later calls.

    This allows users to import pyperclip without having determine_clipboard()
    automatically run, which will automatically select a clipboard mechanism.
    This could be a problem if it selects, say, the memory-heavy PyQt4 module
    but the user was just going to immediately call set_clipboard() to use a
    different clipboard mechanism.

    The lazy loading this stub function implements gives the user a chance to
    call set_clipboard() to pick another clipboard mechanism. Or, if the user
    simply calls copy() or paste() without calling set_clipboard() first,
    will fall back on whatever clipboard mechanism that determine_clipboard()
    automatically chooses.
    '''
    global copy, paste, clear
    copy, paste, clear = determine_clipboard()
    return copy(text)



def lazy_load_stub_paste():
    '''
    A stub function for paste(), which will load the real paste() function when
    called so that the real paste() function is used for later calls.

    This allows users to import pyperclip without having determine_clipboard()
    automatically run, which will automatically select a clipboard mechanism.
    This could be a problem if it selects, say, the memory-heavy PyQt4 module
    but the user was just going to immediately call set_clipboard() to use a
    different clipboard mechanism.

    The lazy loading this stub function implements gives the user a chance to
    call set_clipboard() to pick another clipboard mechanism. Or, if the user
    simply calls copy() or paste() without calling set_clipboard() first,
    will fall back on whatever clipboard mechanism that determine_clipboard()
    automatically chooses.
    '''
    global copy, paste, clear
    copy, paste, clear = determine_clipboard()
    return paste()

def lazy_load_stub_clear():
    '''
    A stub function for clear(), which will load the real clear() function when
    called so that the real clear() function is used for later calls.

    This allows users to import pyperclip without having determine_clipboard()
    automatically run, which will automatically select a clipboard mechanism.
    This could be a problem if it selects, say, the memory-heavy PyQt4 module
    but the user was just going to immediately call set_clipboard() to use a
    different clipboard mechanism.

    The lazy loading this stub function implements gives the user a chance to
    call set_clipboard() to pick another clipboard mechanism. Or, if the user
    simply calls copy() or paste() without calling set_clipboard() first,
    will fall back on whatever clipboard mechanism that determine_clipboard()
    automatically chooses.
    '''
    global copy, paste, clear
    copy, paste, clear = determine_clipboard()
    return clear()

def is_available():
    return copy != lazy_load_stub_copy and paste != lazy_load_stub_paste and clear != lazy_load_stub_clear


# Initially, copy() and paste() are set to lazy loading wrappers which will
# set `copy` and `paste` to real functions the first time they're used, unless
# set_clipboard() or determine_clipboard() is called first.
copy, paste, clear = lazy_load_stub_copy, lazy_load_stub_paste, lazy_load_stub_clear


__all__ = ['copy', 'paste', 'clear', 'set_clipboard', 'determine_clipboard']

