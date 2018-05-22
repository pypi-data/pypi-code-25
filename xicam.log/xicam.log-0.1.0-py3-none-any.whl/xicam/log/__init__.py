import logging

import numpy as np
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from xicam.core import msg

colors = {msg.DEBUG: Qt.gray, msg.ERROR: Qt.darkRed, msg.CRITICAL: Qt.red,
          msg.INFO: Qt.white, msg.WARNING: Qt.yellow}

from xicam.plugins import GUIPlugin, GUILayout


class BlacklistFilter(logging.Filter):
    blacklist = ['ipykernel.inprocess.ipkernel', 'traitlets']

    def filter(self, record):
        return record.name not in self.blacklist


class LogPlugin(GUIPlugin, logging.Handler):
    name = 'Log'
    sigLog = Signal(int, str, str, np.ndarray)

    def __init__(self, *args, **kwargs):
        self.logwidget = QListWidget()
        self.stages = {'Log': GUILayout(self.logwidget)}
        super(LogPlugin, self).__init__(*args, **kwargs)
        logging.Handler.__init__(self)
        self.level = msg.DEBUG
        self.filters = [BlacklistFilter()]

        logging.getLogger().addHandler(self)

    def emit(self, record, level=msg.INFO, timestamp=None, image=None, icon=None):  # We can have icons!
        item = QListWidgetItem(record.msg)
        item.setForeground(QBrush(colors[record.levelno]))
        item.setToolTip(timestamp)
        self.logwidget.addItem(item)
        if image is not None:
            image = np.uint8((image - image.min()) / image.ptp() * 255.0)
            pixmap = QPixmap.fromImage(QImage(image, image.shape[0], image.shape[1], QImage.Format_Indexed8))
            i = QListWidgetItem()
            w = QLabel()
            w.setPixmap(pixmap)
            size = QSize(*image.shape)
            w.setFixedSize(size)
            i.setSizeHint(w.sizeHint())
            self.logwidget.addItem(i)
            self.logwidget.setItemWidget(i, w)
