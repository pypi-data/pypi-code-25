# -*- coding: utf-8 -*-

# Automatically generated - don't edit.
# Use `python setup.py build_ui` to update it.

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.n_clust_label = QtWidgets.QLabel(self.groupBox)
        self.n_clust_label.setObjectName("n_clust_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.n_clust_label)
        self.n_clust_spin = QtWidgets.QSpinBox(self.groupBox)
        self.n_clust_spin.setObjectName("n_clust_spin")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.n_clust_spin)
        self.n_runs_label = QtWidgets.QLabel(self.groupBox)
        self.n_runs_label.setObjectName("n_runs_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.n_runs_label)
        self.n_runs_spin = QtWidgets.QSpinBox(self.groupBox)
        self.n_runs_spin.setObjectName("n_runs_spin")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.n_runs_spin)
        self.n_iter_label = QtWidgets.QLabel(self.groupBox)
        self.n_iter_label.setObjectName("n_iter_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.n_iter_label)
        self.n_iter_spin = QtWidgets.QSpinBox(self.groupBox)
        self.n_iter_spin.setObjectName("n_iter_spin")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.n_iter_spin)
        self.tol_label = QtWidgets.QLabel(self.groupBox)
        self.tol_label.setObjectName("tol_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.tol_label)
        self.tol_dspin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.tol_dspin.setDecimals(6)
        self.tol_dspin.setObjectName("tol_dspin")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.tol_dspin)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(("Form"))
        self.n_clust_label.setText(("# of clusters"))
        self.n_runs_label.setText(("# of runs"))
        self.n_iter_label.setText(("Max. # of iterations"))
        self.tol_label.setText(("Tolerance"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

