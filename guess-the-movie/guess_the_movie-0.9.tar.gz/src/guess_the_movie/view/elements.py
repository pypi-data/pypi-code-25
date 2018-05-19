from PyQt5.QtWidgets import QButtonGroup, QLabel, QWidget, QGridLayout
from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal, QObject, Qt
from PyQt5.QtGui import QResizeEvent
from .. import model


class AnswerButtons(QButtonGroup):
    def __init__(self):
        super(AnswerButtons, self).__init__()

    @pyqtSlot(list)
    def change_labels(self, labels):
        for button, label in zip(self.buttons(), labels):
            button.setText(label)

    def change_colors(self, colors):
        pass


class Screenshot(QLabel):
    def __init__(self, *args, **kwargs):
        super(Screenshot, self).__init__(*args, **kwargs)
        self.__screenshot = None

    @pyqtSlot("QPixmap")
    def set_screenshot(self, screenshot):
        self.__screenshot = screenshot
        self.setPixmap(self.__screenshot.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

    def resizeEvent(self, a0: QResizeEvent):
        super(Screenshot, self).resizeEvent(a0)
        if self.__screenshot is not None:
            self.setPixmap(self.__screenshot.scaled(self.width(), self.height(), Qt.KeepAspectRatio))


class RecordsTable(QWidget):
    def __init__(self, difficult: model.Difficult):
        super(RecordsTable, self).__init__()
        self.difficult = difficult
        self.grid = QGridLayout(self)

        records = model.Records()
        for row in range(records.RECORDS_COUNT_LIMIT):
            name = QLabel("test")
            score = QLabel("0")
            self.grid.addWidget(name, row, 0)
            self.grid.addWidget(score, row, 1)

        records.signals.records_updated.connect(self.update_records)
        self.update_records()

    @pyqtSlot()
    def update_records(self):
        records = model.Records()
        for i, record in enumerate(records.get_records(self.difficult)):
            row = records.RECORDS_COUNT_LIMIT - 1 - i
            if record["score"] > 0:
                name = "{}) {}".format(row + 1, record["name"])
                score = str(record["score"])
            else:
                name, score = "", ""

            self.grid.itemAtPosition(row, 0).widget().setText(name)
            self.grid.itemAtPosition(row, 1).widget().setText(score)





