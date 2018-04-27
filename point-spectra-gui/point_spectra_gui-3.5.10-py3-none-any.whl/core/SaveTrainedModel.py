import pickle
import json
from PyQt5 import QtWidgets, QtGui

from point_spectra_gui.ui.SaveTrainedModel import Ui_Form
from point_spectra_gui.util.Modules import Modules
#from point_spectra_gui.core.MainWindow import MainWindow

class SaveTrainedModel(Ui_Form, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        Modules.setupUi(self, Form)

    def get_widget(self):
        return self.groupBox

    def on_savePushButton_clicked(self, lineEdit):
        self.filename, _filter = QtWidgets.QFileDialog.getSaveFileName(None, "Specify save file name", self.outpath, "(*.tram)")
        lineEdit.setText(self.filename)
        if lineEdit.text() == "":
            lineEdit.setText("*.tram")

    def connectWidgets(self):
        self.setComboBox(self.choosemodel_comboBox, self.modelkeys)
        self.savePushButton.clicked.connect(lambda: self.on_savePushButton_clicked(self.saveLineEdit))

    def run(self):
        modelkey = self.choosemodel_comboBox.currentText()
        # add the data into a list [0. 1]
        # list[0] will hold the dictionary data of the UI
        # TODO Let the user decide what modelkey and model they want to save
        # list[1] will hold the modelkeys
        # list[2] will hold the self.models data
        list = []
        #list.append(json.dumps(MainWindow.getWidgetItems(self), indent=4))
        list.append(modelkey)
        list.append(self.models[modelkey])
        try:
            print(self.filename)
            with open(self.filename, 'wb') as fp:
                pickle.dump(list, fp)
        except Exception as e:
            print("Could not save your trained model: ", e)



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = SaveTrainedModel()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
