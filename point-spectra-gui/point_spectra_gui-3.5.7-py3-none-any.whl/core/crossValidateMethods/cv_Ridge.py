from PyQt5 import QtWidgets, QtCore
from sklearn.linear_model.ridge import Ridge
from sklearn.linear_model.ridge import RidgeCV

from point_spectra_gui.ui.cv_Ridge import Ui_Form
from point_spectra_gui.util.Modules import Modules
import numpy as np

class Ui_Form(Ui_Form, Ridge, RidgeCV, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        self.checkMinAndMax()
        self.connectWidgets()

    def get_widget(self):
        return self.Ridge

    def setHidden(self, bool):
        self.get_widget().setHidden(bool)

    def connectWidgets(self):
        ridge = Ridge()
        self.min_alpha_doubleSpinBox.setDecimals(20)
        self.max_alpha_doubleSpinBox.setDecimals(20)

        self.min_alpha_doubleSpinBox.setValue(0.000000000000001)
        self.max_alpha_doubleSpinBox.setValue(0.01)
        self.n_alpha_spinBox.setValue(100)
        self.fit_intercept_list.setCurrentItem(
            self.fit_intercept_list.findItems(str(ridge.fit_intercept), QtCore.Qt.MatchExactly)[0])
        self.normalize_list.setCurrentItem(
            self.normalize_list.findItems(str(ridge.normalize), QtCore.Qt.MatchExactly)[0])

    def run(self):
        fit_intercept_items = [i.text() == 'True' for i in self.fit_intercept_list.selectedItems()]
        normalize_items = [i.text() == 'True' for i in self.normalize_list.selectedItems()]

        alphas = np.logspace(np.log10(self.min_alpha_doubleSpinBox.value()), np.log10(self.max_alpha_doubleSpinBox.value()),
                             num=self.n_alpha_spinBox.value())
        params = {'alpha': alphas,
                  'fit_intercept': fit_intercept_items,
                  'normalize': normalize_items}
        modelkey = str(params)
        return params, modelkey


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
