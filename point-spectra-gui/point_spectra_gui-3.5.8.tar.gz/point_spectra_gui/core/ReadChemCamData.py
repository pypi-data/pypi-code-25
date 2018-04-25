import pandas as pd
from PyQt5 import QtWidgets
from point_spectra_gui.util.io import io_ccam_pds
from point_spectra_gui.util.spectral_data import spectral_data

from point_spectra_gui.ui.ReadChemCamData import Ui_Form
from point_spectra_gui.util.Modules import Modules


class ReadChemCamData(Ui_Form, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        Modules.setupUi(self, Form)

    def get_widget(self):
        return self.groupBox

    def connectWidgets(self):
        self.searchStringLineEdit.setText("*ccs*.csv")
        self.lookup_col.setText('Spacecraft Clock')
        self.data_col.setText('sclock')
        self.searchDirectorypushButton.clicked.connect(self.on_searchpathButton_clicked)
        self.metadatapushButton.clicked.connect(self.on_metadataButton_clicked)
        self.hide_col_options()
        self.col_check.stateChanged.connect(self.hide_col_options)
    def hide_col_options(self):
        if self.col_check.isChecked():
            self.column_explain.setHidden(False)
            self.data_col.setHidden(False)
            self.lookup_col.setHidden(False)
            self.data_col_label.setHidden(False)
            self.lookup_col_label.setHidden(False)
            self.line.setHidden(False)
        else:
            self.column_explain.setHidden(True)
            self.data_col.setHidden(True)
            self.lookup_col.setHidden(True)
            self.data_col_label.setHidden(True)
            self.lookup_col_label.setHidden(True)
            self.line.setHidden(True)

    def on_searchpathButton_clicked(self):
        dirname = QtWidgets.QFileDialog.getExistingDirectory(parent=None, caption="Select Search Directory",
                                                             directory='.')
        self.searchDirectoryLineEdit.setText(dirname)
        if self.searchDirectoryLineEdit.text() == "":
            self.searchDirectoryLineEdit.setText("*/")

    def on_metadataButton_clicked(self):
        self.metadata_file, null = QtWidgets.QFileDialog.getOpenFileNames(parent=None,
                                                                          caption="Select metadata file(s)",
                                                                          directory='.')
        self.metadataFilesLineEdit.setText(str(self.metadata_file))
        if self.metadataFilesLineEdit.text() == "":
            self.metadataFilesLineEdit.setText("*/")

    def setup(self):
        # TODO this file needs to be redone to fit the similar setup to `LoadData`
        pass


    def run(self):
        params = self.getGuiParams()
        searchdir = self.searchDirectoryLineEdit.text()
        searchstring = self.searchStringLineEdit.text()
        to_csv = self.outputFileNameLineEdit.text()
        left_on = self.data_col.text()
        right_on = self.lookup_col.text()

        try:
            lookupfile = self.metadataFilesLineEdit.text()
            lookupfile = lookupfile[2:-2].split(',')
            lookupfile = [f.strip('\\\' "') for f in lookupfile]
            if lookupfile[0] == '':
                lookupfile = None
        except:
            lookupfile = None
        ave = self.averagesradioButton.isChecked()
        progressbar = QtWidgets.QProgressDialog()
        io_ccam_pds.ccam_batch(searchdir, searchstring=searchstring, to_csv=Modules.outpath + '/' + to_csv,
                               lookupfile=lookupfile, ave=ave, progressbar=progressbar, left_on=left_on, right_on=right_on)
        self.do_get_data(Modules.outpath + '/' + to_csv, 'ChemCam')

    def do_get_data(self, filename, keyname):
        try:
            print('Loading data file: ' + str(filename))
            self.data[keyname] = spectral_data(pd.read_csv(filename, header=[0, 1]))
            self.datakeys.append(keyname)
        except Exception as e:
            print('Problem reading data: {}'.format(e))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    
    Form = QtWidgets.QWidget()
    ui = ReadChemCamData()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
