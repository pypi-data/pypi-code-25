# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'records.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(831, 536)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.toMainMenu = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toMainMenu.sizePolicy().hasHeightForWidth())
        self.toMainMenu.setSizePolicy(sizePolicy)
        self.toMainMenu.setMinimumSize(QtCore.QSize(0, 50))
        self.toMainMenu.setMaximumSize(QtCore.QSize(400, 16777215))
        self.toMainMenu.setObjectName("toMainMenu")
        self.gridLayout.addWidget(self.toMainMenu, 3, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.scrollArea_1 = QtWidgets.QScrollArea(self.tab)
        self.scrollArea_1.setGeometry(QtCore.QRect(10, 10, 781, 371))
        self.scrollArea_1.setWidgetResizable(True)
        self.scrollArea_1.setObjectName("scrollArea_1")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 779, 369))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.scrollArea_1.setWidget(self.scrollAreaWidgetContents_2)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.tab_2)
        self.scrollArea_2.setGeometry(QtCore.QRect(10, 10, 781, 371))
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 779, 369))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_3)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.scrollArea_3 = QtWidgets.QScrollArea(self.tab_3)
        self.scrollArea_3.setGeometry(QtCore.QRect(10, 10, 781, 371))
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName("scrollArea_3")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 779, 369))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents)
        self.tabWidget.addTab(self.tab_3, "")
        self.gridLayout.addWidget(self.tabWidget, 2, 0, 1, 1)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.toMainMenu.setText(_translate("Form", "Назад"))
        self.label_3.setText(_translate("Form", "Рекорды"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Легкий"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Средний"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Form", "Тяжелый"))

