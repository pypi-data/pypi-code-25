from PyQt5 import QtWidgets
from sklearn.neighbors import LocalOutlierFactor
from point_spectra_gui.ui.outliers_LOF import Ui_Form
from point_spectra_gui.util.Modules import Modules


class Ui_Form(Ui_Form, LocalOutlierFactor, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        self.checkMinAndMax()
        self.connectWidgets()

    def get_widget(self):
        return self.groupBox

    def setHidden(self, bool):
        self.get_widget().setHidden(bool)

    def connectWidgets(self):
        self.n_neighbors_spin.setValue(20)
        self.leaf_size_spin.setValue(30)
        self.contamination_spin.setValue(0.1)


    def run(self):
        metric = self.metric_combo.currentText()
        if metric == 'Euclidean':
            p = 2
        if metric == 'Manhattan':
            p = 1

        params = {
            'n_neighbors': self.n_neighbors_spin.value(),
            'contamination': self.contamination_spin.value(),
            'n_jobs': -1,
            'p': p}

        params_key = str(params)
        return params, params_key


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
