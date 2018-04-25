from PyQt5 import QtWidgets

from point_spectra_gui.ui.MaskData import Ui_Form
from point_spectra_gui.util.Modules import Modules
from point_spectra_gui.util.spectral_data import spectral_data
from libpysat.transform.mask import mask


class MaskData(Ui_Form, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        Modules.setupUi(self, Form)

    def get_widget(self):
        return self.groupBox

    def getDataButton_clicked(self, lineEdit):
        filename, _filter = QtWidgets.QFileDialog.getOpenFileName(None, "Open Mask Data File", '.', "(*.csv)")
        lineEdit.setText(filename)
        if lineEdit.text() == "":
            lineEdit.setText("*.csv")

    def connectWidgets(self):
        self.setComboBox(self.chooseDataComboBox, self.datakeys)
        self.pushButton.clicked.connect(lambda: self.getDataButton_clicked(self.maskFileLineEdit))

    def setup(self):
        try:
            self.run() #mask is pretty quick to run, so just call it when running setup
        except:
            pass

    def run(self):
        datakey = self.chooseDataComboBox.currentText()
        maskfile = self.maskFileLineEdit.text()
        self.data[datakey] = spectral_data(mask(self.data[datakey].df, maskfile, maskvar='wvl'))
        print("Mask applied")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    Form = QtWidgets.QWidget()
    ui = MaskData()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
