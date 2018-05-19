# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'game_over.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 219)
        self.name_textbox = QtWidgets.QLineEdit(Dialog)
        self.name_textbox.setGeometry(QtCore.QRect(30, 120, 341, 31))
        self.name_textbox.setObjectName("name_textbox")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(120, 10, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(30, 170, 341, 30))
        self.pushButton.setObjectName("pushButton")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(30, 50, 101, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.score = QtWidgets.QLabel(Dialog)
        self.score.setGeometry(QtCore.QRect(310, 50, 53, 17))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.score.setFont(font)
        self.score.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.score.setObjectName("score")
        self.new_record_label = QtWidgets.QLabel(Dialog)
        self.new_record_label.setGeometry(QtCore.QRect(120, 80, 171, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.new_record_label.setFont(font)
        self.new_record_label.setObjectName("new_record_label")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(30, 70, 341, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.name_textbox.setPlaceholderText(_translate("Dialog", "Введите ваше  имя"))
        self.label.setText(_translate("Dialog", "Игра окончена"))
        self.pushButton.setText(_translate("Dialog", "Заново"))
        self.label_2.setText(_translate("Dialog", "Ваш счет:"))
        self.score.setText(_translate("Dialog", "100"))
        self.new_record_label.setText(_translate("Dialog", "Новый рекорд!"))

