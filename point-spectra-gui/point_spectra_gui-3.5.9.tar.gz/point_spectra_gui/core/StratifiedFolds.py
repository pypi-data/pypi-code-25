from PyQt5 import QtWidgets

from point_spectra_gui.ui.StratifiedFolds import Ui_Form
from point_spectra_gui.util.Modules import Modules
from point_spectra_gui.util.spectral_data import spectral_data
from libpysat.utils.folds import stratified_folds
from libpysat.utils.utils import rows_match
import copy

class StratifiedFolds(Ui_Form, Modules):
    count = -1

    def __init__(self):
        StratifiedFolds.count += 1
        self.curr_count = StratifiedFolds.count
        print('Added StratifiedFolds with ID {}'.format(self.curr_count))

    def delete(self):
        try:
            StratifiedFolds.count -= 1
            del self.data[self.datakeys[-1]]
            del self.datakeys[-1]
        except IndexError:
            pass

    def setupUi(self, Form):
        super().setupUi(Form)
        Modules.setupUi(self, Form)

    def get_widget(self):
        return self.formGroupBox

    def connectWidgets(self):
        self.nFoldsSpinBox.setValue(2)
        self.testFoldsSpinBox.setValue(2)
        self.setComboBox(self.chooseDataToStratifyComboBox, self.datakeys)
        try:  # Some instances where perhaps there is no data to load
            data = self.data[self.chooseDataToStratifyComboBox.currentText()].df['comp'].columns.values
            self.setComboBox(self.chooseVarComboBox, data)
        except:
            pass
        self.chooseDataToStratifyComboBox.activated[int].connect(self.strat_fold_change_vars)
        self.nFoldsSpinBox.valueChanged.connect(self.strat_fold_change_testfolds)

    def setup(self):
        try:
            datakey = self.chooseDataToStratifyComboBox.currentText()

            self.data[datakey + '-Train'] = copy.deepcopy(self.data[datakey])
            self.data[datakey + '-Test'] = copy.deepcopy(self.data[datakey])
            if datakey + '-Train' not in self.datakeys and datakey + '-Test' not in self.datakeys:
                self.datakeys.append(datakey + '-Train')
                self.datakeys.append(datakey + '-Test')
        except:
            pass

    def run(self):
        datakey = self.chooseDataToStratifyComboBox.currentText()
        nfolds = self.nFoldsSpinBox.value()
        try:
            testfold = int(self.testFoldsSpinBox.value())
        except:
            testfold = 1
        colname = ('comp', self.chooseVarComboBox.currentText())
        self.data[datakey]=spectral_data(stratified_folds(self.data[datakey].df,nfolds=nfolds, sortby=colname))

        self.data[datakey + '-Train'] = spectral_data(rows_match(self.data[datakey].df,('meta', 'Folds'), [testfold], invert=True))
        self.data[datakey + '-Test'] = spectral_data(rows_match(self.data[datakey].df,('meta', 'Folds'), [testfold]))
        self.datakeys.append(datakey + '-Train')
        self.datakeys.append(datakey + '-Test')

        print(self.data.keys())
        print(self.data[datakey + '-Test'].df.index.shape)
        print(self.data[datakey + '-Train'].df.index.shape)

    def strat_fold_change_vars(self):
        self.chooseVarComboBox.clear()
        try:
            choices = self.data[self.chooseDataToStratifyComboBox.currentText()].df['comp'].columns.values
        except:
            choices = ['No composition columns!']

        self.chooseVarComboBox.addItems(choices)

    def strat_fold_change_testfolds(self):
        self.testFoldsSpinBox.setMaximum(self.nFoldsSpinBox.value())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    Form = QtWidgets.QWidget()
    ui = StratifiedFolds()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
