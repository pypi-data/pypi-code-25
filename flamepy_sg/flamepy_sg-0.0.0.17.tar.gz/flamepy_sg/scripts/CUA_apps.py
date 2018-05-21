from flamepy_sg.scripts.customprints.ansi_colors import sg_colors

# PySide stuff, included with Flame default install. Quick and lazy import*
from PySide.QtCore import *
from PySide.QtGui import *

print sg_colors.grey3 + '-' * 80 + sg_colors.endc
print sg_colors.blue2 + "--- From CUA_apps ---" + sg_colors.endc

# adds entries to Flame contextual menu.


def getCustomUIActions():

    appsAction1 = {}
    appsAction1["name"] = "screenshot"
    appsAction1["caption"] = "Screenshot"

    appsGroup = {}
    appsGroup["name"] = "Apps"
    appsGroup["actions"] = (appsAction1,)

    return (appsGroup, )

# Assign some action to the CUA (customUIAction) menu entries


def customUIAction(info, userData):

    if info['name'] == 'screenshot':

        class Screenshot(QWidget):
            def __init__(self):
                super(Screenshot, self).__init__()

                self.screenshotLabel = QLabel()
                self.screenshotLabel.setSizePolicy(QSizePolicy.Expanding,
                                                   QSizePolicy.Expanding)
                self.screenshotLabel.setAlignment(Qt.AlignCenter)
                self.screenshotLabel.setMinimumSize(240, 160)

                self.createOptionsGroupBox()
                self.createButtonsLayout()

                mainLayout = QVBoxLayout()
                mainLayout.addWidget(self.screenshotLabel)
                mainLayout.addWidget(self.optionsGroupBox)
                mainLayout.addLayout(self.buttonsLayout)
                self.setLayout(mainLayout)

                self.shootScreen()
                self.delaySpinBox.setValue(5)

                self.setWindowTitle("Screenshot")
                self.resize(300, 200)

            def resizeEvent(self, event):
                scaledSize = self.originalPixmap.size()
                scaledSize.scale(self.screenshotLabel.size(), Qt.KeepAspectRatio)
                if not self.screenshotLabel.pixmap() or scaledSize != self.screenshotLabel.pixmap().size():
                    self.updateScreenshotLabel()

            def newScreenshot(self):
                if self.hideThisWindowCheckBox.isChecked():
                    self.hide()
                self.newScreenshotButton.setDisabled(True)

                QTimer.singleShot(self.delaySpinBox.value() * 1000,
                                  self.shootScreen)

            def saveScreenshot(self):
                format = 'png'
                initialPath = QDir.currentPath() + "/untitled." + format

                fileName, _ = QFileDialog.getSaveFileName(self, "Save As",
                                                          initialPath,
                                                          "%s Files (*.%s);;All Files (*)" % (format.upper(), format))
                if fileName:
                    self.originalPixmap.save(fileName, format)

            def shootScreen(self):
                if self.delaySpinBox.value() != 0:
                    qApp.beep()

                # Garbage collect any existing image first.
                self.originalPixmap = None
                self.originalPixmap = QPixmap.grabWindow(QApplication.desktop().winId())
                self.updateScreenshotLabel()

                self.newScreenshotButton.setDisabled(False)
                if self.hideThisWindowCheckBox.isChecked():
                    self.show()

            def updateCheckBox(self):
                if self.delaySpinBox.value() == 0:
                    self.hideThisWindowCheckBox.setDisabled(True)
                else:
                    self.hideThisWindowCheckBox.setDisabled(False)

            def createOptionsGroupBox(self):
                self.optionsGroupBox = QGroupBox("Options")

                self.delaySpinBox = QSpinBox()
                self.delaySpinBox.setSuffix(" s")
                self.delaySpinBox.setMaximum(60)
                self.delaySpinBox.valueChanged.connect(self.updateCheckBox)

                self.delaySpinBoxLabel = QLabel("Screenshot Delay:")

                self.hideThisWindowCheckBox = QCheckBox("Hide This Window")

                optionsGroupBoxLayout = QGridLayout()
                optionsGroupBoxLayout.addWidget(self.delaySpinBoxLabel, 0, 0)
                optionsGroupBoxLayout.addWidget(self.delaySpinBox, 0, 1)
                optionsGroupBoxLayout.addWidget(self.hideThisWindowCheckBox, 1, 0, 1, 2)
                self.optionsGroupBox.setLayout(optionsGroupBoxLayout)

            def createButtonsLayout(self):
                self.newScreenshotButton = self.createButton("New Screenshot",
                                                             self.newScreenshot)

                self.saveScreenshotButton = self.createButton("Save Screenshot",
                                                              self.saveScreenshot)

                self.quitScreenshotButton = self.createButton("Quit", self.close)

                self.buttonsLayout = QHBoxLayout()
                self.buttonsLayout.addStretch()
                self.buttonsLayout.addWidget(self.newScreenshotButton)
                self.buttonsLayout.addWidget(self.saveScreenshotButton)
                self.buttonsLayout.addWidget(self.quitScreenshotButton)

            def createButton(self, text, member):
                button = QPushButton(text)
                button.clicked.connect(member)
                return button

            def updateScreenshotLabel(self):
                self.screenshotLabel.setPixmap(self.originalPixmap.scaled(
                    self.screenshotLabel.size(), Qt.KeepAspectRatio,
                    Qt.SmoothTransformation))

        # app = QApplication(sys.argv)
        form = Screenshot()
        form.show()
        # sys.exit(app.exec_())
        app.exec_()


# print 'End of CustomUIAction_Utilities:'
print sg_colors.orange1 + "--- End of CUA_apps ---" + sg_colors.endc
print sg_colors.grey3 + '-' * 80 + sg_colors.endc
