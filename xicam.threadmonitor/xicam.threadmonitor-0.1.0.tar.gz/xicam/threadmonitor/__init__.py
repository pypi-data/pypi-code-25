from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from xicam.gui.static import path
from xicam.gui.threads import manager as threadmanager
from xicam.plugins import GUIPlugin, GUILayout


class ThreadMonitorPlugin(GUIPlugin):
    name = 'Thread Monitor'

    def __init__(self):
        self.monitorwidget = QListView()
        self.toolbar = QToolBar()
        actionPause = QAction(QIcon(str(path('icons/pause.png'))), "Pause", self.toolbar)
        actionPause.triggered.connect(self.pause)
        actionPause.setCheckable(True)
        self.toolbar.addAction(actionPause)
        self.stages = {'Monitor': GUILayout(self.monitorwidget, top=self.toolbar)}
        super(ThreadMonitorPlugin, self).__init__()

        self.model = QStandardItemModel()
        self.monitorwidget.setModel(self.model)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start()

    def update(self):
        # TODO: check if this plugin is active

        self.model.clear()
        for thread in threadmanager.threads:
            item = QStandardItem(thread.method.__repr__())
            item.setData(QColor(Qt.gray), Qt.ForegroundRole)
            if thread.running:
                item.setData(QColor(Qt.yellow), Qt.ForegroundRole)
            if thread.cancelled:
                item.setData(QColor(Qt.magenta), Qt.ForegroundRole)
            if thread.exception:
                item.setData(QColor(Qt.red), Qt.ForegroundRole)
            if thread.done:
                item.setData(QColor(Qt.green), Qt.ForegroundRole)
            self.model.appendRow(item)

    def _test(self):

        from xicam.gui import threads
        import time
        def test():
            a = 0
            for i in range(10):
                a += 1
                time.sleep(1)

        for i in range(100):
            t = threads.QThreadFuture(test)
            t.start()
