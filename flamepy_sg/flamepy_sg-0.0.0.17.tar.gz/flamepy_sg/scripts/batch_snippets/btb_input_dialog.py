
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtCore, QtGui
import sys
import os

# turn the relative __file__ value into it's full path
absolute_path = os.path.realpath(__file__)
# Use the os module to split the filepath using '/' as a seperator to creates a list from which we pick IDs []
root_path = '/'.join(absolute_path.split('/')[0:-4])

# navigate down to the desired folder
sys.path.append("{root}/flamepy_sg/modules".format(root=root_path))

from flamepy_sg.scripts.customprints.ansi_colors import sg_colors as sg_colors


class InputDialogBox(QDialog):

    # print "\x1b[38;5;226m --- Running class InputDialogBox(QDialog): in input_dialog.py --- \x1b[0m"
    print sg_colors.green1 + "--- Running class InputDialogBox(QDialog): in input_dialog.py ---" + sg_colors.endc

    def __init__(self, parent=None):
        super(InputDialogBox, self).__init__(parent)

        # print "\x1b[38;5;229m --- Running def ___init___ in class InputDialogBox(QDialog): in input_dialog.py --- \x1b[0m"
        print sg_colors.green1 + "--- Running def ___init___ in class InputDialogBox(QDialog): in input_dialog.py ---" + sg_colors.endc

        self.setWindowTitle("Shot & Element names.")

        self.shotName = QLineEdit()
        self.shotLabel = QLabel('Shot name:')
        self.shotInput = self.shotName.text()
        self.elementName = QLineEdit()
        self.elementLabel = QLabel('Element name:')
        self.elementInput = self.elementName.text()
        buttonOk = QPushButton("OK")
        buttonCancel = QPushButton("Cancel")

        layout = QGridLayout()
        layout.addWidget(self.shotLabel, 0, 0)
        layout.addWidget(self.shotName, 0, 1)
        layout.addWidget(self.elementLabel, 1, 0)
        layout.addWidget(self.elementName, 1, 1)
        layout.addWidget(buttonOk)
        layout.addWidget(buttonCancel)

        self.setLayout(layout)

        self.connect(buttonOk, SIGNAL("clicked()"), self, SLOT("accept()"))
        self.connect(buttonCancel, SIGNAL("clicked()"), self, SLOT("reject()"))

        # print "\x1b[38;5;202m --- End of def def ___init___ in class InputDialogBox(QDialog): in input_dialog.py --- \x1b[0m"
        print sg_colors.orange1 + "--- End of def def ___init___ in class InputDialogBox(QDialog): in input_dialog.py ---" + sg_colors.endc
        print sg_colors.grey3 + '-' * 80 + sg_colors.endc
