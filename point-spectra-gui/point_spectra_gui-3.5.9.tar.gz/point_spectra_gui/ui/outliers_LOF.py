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
        self.n_neighbors_label = QtWidgets.QLabel(self.groupBox)
        self.n_neighbors_label.setObjectName("n_neighbors_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.n_neighbors_label)
        self.n_neighbors_spin = QtWidgets.QSpinBox(self.groupBox)
        self.n_neighbors_spin.setMinimum(1)
        self.n_neighbors_spin.setMaximum(99999999)
        self.n_neighbors_spin.setProperty("value", 20)
        self.n_neighbors_spin.setObjectName("n_neighbors_spin")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.n_neighbors_spin)
        self.leaf_size_label = QtWidgets.QLabel(self.groupBox)
        self.leaf_size_label.setToolTip("")
        self.leaf_size_label.setObjectName("leaf_size_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.leaf_size_label)
        self.leaf_size_spin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.leaf_size_spin.setDecimals(4)
        self.leaf_size_spin.setMaximum(0.5)
        self.leaf_size_spin.setObjectName("leaf_size_spin")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.leaf_size_spin)
        self.metric_combo = QtWidgets.QComboBox(self.groupBox)
        self.metric_combo.setObjectName("metric_combo")
        self.metric_combo.addItem("")
        self.metric_combo.addItem("")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.metric_combo)
        self.metric_label = QtWidgets.QLabel(self.groupBox)
        self.metric_label.setObjectName("metric_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.metric_label)
        self.contamination_label = QtWidgets.QLabel(self.groupBox)
        self.contamination_label.setObjectName("contamination_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.contamination_label)
        self.contamination_spin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.contamination_spin.setObjectName("contamination_spin")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.contamination_spin)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(("Form"))
        self.n_neighbors_label.setText(("# of neighbors"))
        self.leaf_size_label.setText(("Leaf size"))
        self.metric_combo.setItemText(0, ("Euclidean"))
        self.metric_combo.setItemText(1, ("Manhattan"))
        self.metric_label.setText(("Distance Metric"))
        self.contamination_label.setText(("Fraction of outliers"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

