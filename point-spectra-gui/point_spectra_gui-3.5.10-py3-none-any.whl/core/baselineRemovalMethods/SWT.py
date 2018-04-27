from PyQt5 import QtWidgets
from libpysat.transform.baseline_code.ccam_remove_continuum import ccam_br

from point_spectra_gui.ui.SWT import Ui_Form
from point_spectra_gui.util.Modules import Modules


class Ui_Form(Ui_Form, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        self.checkMinAndMax()
        Modules.setupUi(self, Form)

    def get_widget(self):
        return self.groupBox

    def setHidden(self, bool):
        self.get_widget().setHidden(bool)

    def connectWidgets(self):
        SWT = ccam_br()
        self.lowestWaveletScaleSpinBox.setValue(SWT.lvmin_)
        self.largestWaveletScaleSpinBox.setValue(SWT.lv_)

    def run(self):
        methodParameters = {'lv_': self.largestWaveletScaleSpinBox.value(),
                            'lvmin_': self.lowestWaveletScaleSpinBox.value()}

        int_flag = self.interpolationMethodComboBox.currentText()
        if int_flag == 'Linear':
            methodParameters.update({'int_flag_': 0})
        elif int_flag == 'Quadratic':
            methodParameters.update({'int_flag_': 1})
        elif int_flag == 'Spline':
            methodParameters.update({'int_flag_': 2})

        return methodParameters, self.getChangedValues(methodParameters, ccam_br())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
