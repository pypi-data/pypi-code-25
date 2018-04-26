from PyQt5 import QtWidgets
from sklearn.decomposition.pca import PCA
from point_spectra_gui.ui.cluster_KMeans import Ui_Form
from point_spectra_gui.util.Modules import Modules


class Ui_Form(Ui_Form, PCA, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        self.checkMinAndMax()
        self.connectWidgets()

    def get_widget(self):
        return self.groupBox

    def setHidden(self, bool):
        self.get_widget().setHidden(bool)

    def connectWidgets(self):
        self.n_clust_spin.setValue(8)
        self.n_runs_spin.setValue(10)
        self.n_iter_spin.setValue(300)
        self.tol_dspin.setValue(0.0001)

    def run(self):
        params = {
            'n_clusters': self.n_clust_spin.value(),
            'n_init': self.n_runs_spin.value(),
            'max_iter': self.n_iter_spin.value(),
            'tol': self.tol_dspin.value(),
            'n_jobs': -2} #use all but one cpu in parallel
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
