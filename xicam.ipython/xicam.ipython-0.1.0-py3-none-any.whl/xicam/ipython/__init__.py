import sys

# Hack to work around PySide being imported from nowhere:
import qtpy

from xicam.plugins import GUIPlugin, GUILayout
from xicam.plugins import manager as pluginmanager
from xicam.plugins import observers as pluginobservers

# Note: qtconsole often fails to guess correctly which qt flavor to use. One of the below snippets will guide it.

# Overload for Py2App
# def new_load_qt(api_options):
#     from qtpy import QtCore, QtWidgets, QtSvg
#
#     return QtCore, QtWidgets, QtGuiCompat, 'pyqt5'
# from qtconsole import qt_loaders
# qt_loaders.load_qt(['pyqt5'])
if 'PySide.QtCore' in sys.modules and qtpy.API != 'pyside': del sys.modules['PySide.QtCore']

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager


class IPythonPlugin(GUIPlugin):
    name = 'ipython'

    def __init__(self):
        # # Enforce global style within the console
        # with open('xicam/gui/style.stylesheet', 'r') as f:
        #     style = f.read()
        # style = (qdarkstyle.load_stylesheet() + style)

        # Setup the kernel
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        kernel = self.kernel_manager.kernel
        kernel.gui = 'qt'

        # Push Xi-cam variables into the kernel
        kernel.shell.push({plugin.name: plugin for plugin in pluginmanager.getPluginsOfCategory("GUIPlugin")})

        # Observe plugin changes
        pluginobservers.append(self)

        # Continue kernel setuppluginmanager.getPluginsOfCategory("GUIPlugin")
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()

        # Setup console widgets
        def stop():
            self.kernel_client.stop_channels()
            self.kernel_manager.shutdown_kernel()
        control = RichJupyterWidget()
        control.kernel_manager = self.kernel_manager
        control.kernel_client = self.kernel_client
        control.exit_requested.connect(stop)
        # control.style_sheet = style
        control.syntax_style = u'monokai'
        control.set_default_style(colors='Linux')

        # Setup layout
        self.stages = {'Terminal': GUILayout(control)}

        # Save for later
        self.kernel = kernel

        super(IPythonPlugin, self).__init__()

    def pluginsChanged(self):
        self.kernel.shell.push({plugin.name: plugin for plugin in pluginmanager.getPluginsOfCategory("GUIPlugin")})
