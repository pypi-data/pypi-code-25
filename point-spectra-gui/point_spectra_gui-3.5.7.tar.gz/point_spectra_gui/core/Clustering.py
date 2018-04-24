from PyQt5 import QtWidgets

from point_spectra_gui.util import Qtickle
from point_spectra_gui.core.clusteringMethods import *
from point_spectra_gui.ui.Clustering import Ui_Form
from point_spectra_gui.util.Modules import Modules
from libpysat.clustering.cluster import cluster
from point_spectra_gui.util.spectral_data import spectral_data


class Clustering(Ui_Form, Modules):
    def setupUi(self, Form):
        self.Form = Form
        super().setupUi(Form)
        Modules.setupUi(self, Form)
        self.clusteringMethods()

    def get_widget(self):
        return self.formGroupBox

    def connectWidgets(self):
        self.algorithm_list = ['Choose an algorithm',
                               'K-Means',
                               'Spectral'
                               ]

        self.setComboBox(self.chooseDataComboBox, self.datakeys)
        self.setListWidget(self.variables_list, self.xvar_choices())
        self.chooseDataComboBox.currentIndexChanged.connect(
            lambda: self.changeComboListVars(self.variables_list, self.xvar_choices()))
        self.setComboBox(self.chooseMethodComboBox, self.algorithm_list)
        self.chooseMethodComboBox.currentIndexChanged.connect(
            lambda: self.make_cluster_widget(self.chooseMethodComboBox.currentText()))

    def getGuiParams(self):
        """
        Overriding Modules' getGuiParams, because I'll need to do a list of lists
        in order to obtain the regressionMethods' parameters
        """
        self.qt = Qtickle.Qtickle(self)
        s = []
        s.append(self.qt.guiSave())
        for items in self.alg:
            s.append(items.getGuiParams())
        return s

    def setGuiParams(self, dict):
        """
        Overriding Modules' setGuiParams, because we are accessing a list of lists
        And each submodule contains it's own `setGuiParams`
        """
        self.qt = Qtickle.Qtickle(self)
        self.qt.guiRestore(dict[0])
        for i in range(len(dict)):
            self.alg[i - 1].setGuiParams(dict[i])

    def selectiveSetGuiParams(self, dict):
        """
        Override Modules' selective Restore function

        Setup Qtickle
        selectively restore the UI, the data to do that will be in the 0th element of the dictionary
        We will then iterate through the rest of the dictionary
        Will now restore the parameters for the algorithms in the list, Each of the algs have their own selectiveSetGuiParams

        :param dict:
        :return:
        """

        self.qt = Qtickle.Qtickle(self)
        self.qt.selectiveGuiRestore(dict[0])
        for i in range(len(dict)):
            self.alg[i - 1].selectiveSetGuiParams(dict[i])

    def setup(self):
        method = self.chooseMethodComboBox.currentText()
        datakey = self.chooseDataComboBox.currentText()
        if method != 'Choose an algorithm':
            self.data[datakey].df[(method, 'Cluster')] = 99999  # create the column to hold the clustering results,
            # fill with dummy data until clustering is actually run

    def run(self):
        method = self.chooseMethodComboBox.currentText()
        datakey = self.chooseDataComboBox.currentText()
        params, modelkey = self.getMethodParams(self.chooseMethodComboBox.currentIndex())
        col = [str(i.text()) for i in self.variables_list.selectedItems()]
        self.data[datakey] = spectral_data(cluster(self.data[datakey].df, col, method, [], params))

    def make_cluster_widget(self, alg):
        self.hideAll()
        # print(alg)
        for i in range(len(self.algorithm_list)):
            if alg == self.algorithm_list[i] and i > 0:
                self.alg[i - 1].setHidden(False)

    def hideAll(self):
        for a in self.alg:
            a.setHidden(True)

    def clusteringMethods(self):
        self.alg = []
        list_forms = [cluster_KMeans,
                      cluster_Spectral]
        for items in list_forms:
            self.alg.append(items.Ui_Form())
            self.alg[-1].setupUi(self.Form)
            self.clustering_vlayout.addWidget(self.alg[-1].get_widget())
            self.alg[-1].setHidden(True)

    def getMethodParams(self, index):
        return self.alg[index - 1].run()

    def xvar_choices(self):
        try:
            try:
                xvarchoices = self.data[self.chooseDataComboBox.currentText()].df.columns.levels[0].values
            except:
                xvarchoices = self.data[self.chooseDataComboBox.currentText()].columns.values
            xvarchoices = [i for i in xvarchoices if not 'Unnamed' in i]  # remove unnamed columns from choices
        except:
            xvarchoices = ['No valid choices!']
        return xvarchoices


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    Form = QtWidgets.QWidget()
    ui = Clustering()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
