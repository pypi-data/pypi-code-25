# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_menu.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(796, 839)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(520, 280))
        self.groupBox.setMaximumSize(QtCore.QSize(520, 320))
        self.groupBox.setObjectName("groupBox")
        self.newGameButton = QtWidgets.QPushButton(self.groupBox)
        self.newGameButton.setGeometry(QtCore.QRect(60, 100, 399, 60))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newGameButton.sizePolicy().hasHeightForWidth())
        self.newGameButton.setSizePolicy(sizePolicy)
        self.newGameButton.setMaximumSize(QtCore.QSize(400, 60))
        self.newGameButton.setObjectName("newGameButton")
        self.recordsButton = QtWidgets.QPushButton(self.groupBox)
        self.recordsButton.setGeometry(QtCore.QRect(60, 170, 399, 60))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.recordsButton.sizePolicy().hasHeightForWidth())
        self.recordsButton.setSizePolicy(sizePolicy)
        self.recordsButton.setMaximumSize(QtCore.QSize(400, 60))
        self.recordsButton.setObjectName("recordsButton")
        self.exitButton = QtWidgets.QPushButton(self.groupBox)
        self.exitButton.setGeometry(QtCore.QRect(60, 240, 399, 60))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exitButton.sizePolicy().hasHeightForWidth())
        self.exitButton.setSizePolicy(sizePolicy)
        self.exitButton.setMaximumSize(QtCore.QSize(400, 60))
        self.exitButton.setObjectName("exitButton")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(190, 40, 141, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.groupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.newGameButton.setText(_translate("Form", "Новая игра"))
        self.recordsButton.setText(_translate("Form", "Рекорды"))
        self.exitButton.setText(_translate("Form", "Выход"))
        self.label.setText(_translate("Form", "Главное меню"))

