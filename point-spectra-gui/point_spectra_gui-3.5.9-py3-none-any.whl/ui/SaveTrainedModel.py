# -*- coding: utf-8 -*-

# Automatically generated - don't edit.
# Use `python setup.py build_ui` to update it.

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.saveLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.saveLineEdit.setFrame(True)
        self.saveLineEdit.setReadOnly(True)
        self.saveLineEdit.setObjectName("saveLineEdit")
        self.gridLayout.addWidget(self.saveLineEdit, 1, 0, 1, 1)
        self.savePushButton = QtWidgets.QPushButton(self.groupBox)
        self.savePushButton.setMaximumSize(QtCore.QSize(30, 16777215))
        self.savePushButton.setObjectName("savePushButton")
        self.gridLayout.addWidget(self.savePushButton, 1, 1, 1, 1)
        self.choosemodel_comboBox = QtWidgets.QComboBox(self.groupBox)
        self.choosemodel_comboBox.setObjectName("choosemodel_comboBox")
        self.gridLayout.addWidget(self.choosemodel_comboBox, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(("Form"))
        self.groupBox.setTitle(("Save a Trained Model"))
        self.savePushButton.setText(("..."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

