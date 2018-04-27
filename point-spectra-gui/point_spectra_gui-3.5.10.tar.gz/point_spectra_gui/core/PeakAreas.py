import numpy as np
from PyQt5 import QtWidgets
import pandas as pd
from point_spectra_gui.ui.PeakAreas import Ui_Form
from point_spectra_gui.util.Modules import Modules
from point_spectra_gui.util.spectral_data import spectral_data
from libpysat.transform.peak_area import peak_area

class PeakAreas(Ui_Form, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        Modules.setupUi(self, Form)

    def get_widget(self):
        return self.groupBox

    def connectWidgets(self):
        self.peakMinimaLineEdit.setText("None (calculate from average spectrum)")
        self.setComboBox(self.chooseDataComboBox, self.datakeys)
        self.pushButton.clicked.connect(lambda: self.on_getDataButton_clicked(self.peakMinimaLineEdit))

    def setup(self):
        datakey = self.chooseDataComboBox.currentText()
        self.data[datakey].df[('peak_area',99999)] = 99999  #create a dummy column so that "peak_Area" shows up as an option in later modules

    def run(self):
        datakey = self.chooseDataComboBox.currentText()
        peaks_mins_file = self.peakMinimaLineEdit.text()
        if peaks_mins_file == "None (calculate from average spectrum)":
            peaks_mins_file = None

        try:
            self.data[datakey].peak_area(peaks_mins_file)
            print("Peak Areas Calculated")
            output = pd.DataFrame(columns = ['peaks','mins'])
            output['peaks'] = self.data[datakey].peaks
            output['mins'] = np.append(self.data[datakey].mins,np.nan)
            output.to_csv(self.outpath+'/peaks_mins.csv')
            print('Peaks and mins saved to '+self.outpath+'/peaks_mins.csv')

        except Exception as e:
            print(e)

    def on_getDataButton_clicked(self, lineEdit):
        filename, _filter = QtWidgets.QFileDialog.getOpenFileName(None, "Open peaks and minima File", '.', "(*.csv)")
        lineEdit.setText(filename)
        if lineEdit.text() == "":
            lineEdit.setText("None (calculate from average spectrum)")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    Form = QtWidgets.QWidget()
    ui = PeakAreas()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
