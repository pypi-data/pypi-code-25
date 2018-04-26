import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from point_spectra_gui.util import Qtickle
from libpysat.regression import cv
from point_spectra_gui.util.spectral_data import spectral_data
from point_spectra_gui.core.crossValidateMethods import *
from point_spectra_gui.ui.CrossValidation import Ui_Form
from point_spectra_gui.util.Modules import Modules
from sklearn.model_selection import ParameterGrid, LeaveOneGroupOut


class CrossValidation(Ui_Form, Modules):
    count = -1

    def setupUi(self, Form):
        self.Form = Form
        super().setupUi(Form)
        Modules.setupUi(self, Form)
        self.regressionMethods()

    def get_widget(self):
        return self.groupLayout

    def make_regression_widget(self, alg, params=None):
        self.hideAll()
        print(alg)
        try:
            self.alg[alg].setHidden(False)
        except:
            pass

    def connectWidgets(self):
        self.algorithm_list = ['Choose an algorithm',
                               'ARD',
                               'BRR',
                               'Elastic Net',
                               'GP',
                               # 'KRR',  This needs more work since it requires parameters for the kernel passed as an object
                               'LARS',
                               'LASSO',
                               # 'LASSO LARS', - this also need to be debugged
                               'OLS',
                               'OMP',
                               'PLS',
                               'Ridge',
                               'SVR']

        self.setComboBox(self.chooseDataComboBox, self.datakeys)
        self.setComboBox(self.chooseAlgorithmComboBox, self.algorithm_list)
        self.yMaxDoubleSpinBox.setMaximum(999999)
        self.yMinDoubleSpinBox.setMaximum(999999)
        self.yMaxDoubleSpinBox.setValue(100)
        self.changeComboListVars(self.yVariableList, self.yvar_choices())
        self.changeComboListVars(self.xVariableList, self.xvar_choices())
        self.xvar_choices()
        self.chooseAlgorithmComboBox.currentIndexChanged.connect(
            lambda: self.make_regression_widget(self.chooseAlgorithmComboBox.currentText()))
        self.chooseDataComboBox.currentIndexChanged.connect(
            lambda: self.changeComboListVars(self.yVariableList, self.yvar_choices()))
        self.chooseDataComboBox.currentIndexChanged.connect(
            lambda: self.changeComboListVars(self.xVariableList, self.xvar_choices()))

    def getGuiParams(self):
        """
        Overriding Modules' getGuiParams, because I'll need to do a list of lists
        in order to obtain the regressionMethods' parameters
        """
        self.qt = Qtickle.Qtickle(self)
        s = []
        s.append(self.qt.guiSave())
        for items in self.alg:
            s.append(self.alg[items].getGuiParams())
        return s

    def setGuiParams(self, dict):
        self.qt = Qtickle.Qtickle(self)
        self.qt.guiRestore(dict[0])
        keys = list(self.alg.keys())
        for i in range(len(dict)):
            self.alg[keys[i - 1]].setGuiParams(dict[i])

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
        keys = list(self.alg.keys())
        for i in range(len(dict)):
            self.alg[keys[i - 1]].selectiveSetGuiParams(dict[i])

    def setup(self):
        try:
            method = self.chooseAlgorithmComboBox.currentText()
            datakey = self.chooseDataComboBox.currentText()
            xvars = [str(x.text()) for x in self.xVariableList.selectedItems()]
            yvars = [('comp', str(y.text())) for y in self.yVariableList.selectedItems()]
            yrange = [self.yMinDoubleSpinBox.value(), self.yMaxDoubleSpinBox.value()]
            # Warning: Params passing through cv.cv(params) needs to be in lists
            # Example: {'n_components': [4], 'scale': [False]}
            params, modelkey = self.alg[self.chooseAlgorithmComboBox.currentText()].run()

            #if the method supports it, separate out alpha from the other parameters and prepare for calculating path
            path_methods =  ['Elastic Net', 'LASSO']#, 'Ridge']
            if method in path_methods:
                alphas = params.pop('alpha')
            else:
                alphas = None

            paramgrid = list(ParameterGrid(params))  # create a grid of parameter permutations
            cv_obj = cv.cv(paramgrid)
            cvpredictkeys = []
            cvmodelkeys = []
            for i in range(len(paramgrid)):
                if alphas is not None:
                    for j in range(len(alphas)):
                        keytemp = '"' + method + ' - ' + yvars[0][-1] + ' - CV - Alpha:' + str(alphas[j]) + ' - ' + str(paramgrid[i]) + '"'
                        cvpredictkeys.append(keytemp)
                        keytemp = '"' + method + ' - ' + yvars[0][-1] + ' - Cal - Alpha:' + str(
                            alphas[j]) + ' - ' + str(paramgrid[i]) + '"'
                        cvpredictkeys.append(keytemp)

                        modelkeytemp = "{} - {} - ({}, {}) Alpha: {}, {}".format(method, yvars[0][-1], yrange[0], yrange[1],
                                                                             alphas[j], paramgrid[i])
                        cvmodelkeys.append(modelkeytemp)

                else:
                    keytemp = '"'+method+'- Cal -' + str(paramgrid[i]) + '"'
                    cvpredictkeys.append(keytemp)
                    keytemp = '"' + method + '- Cal -' + str(paramgrid[i]) + '"'
                    cvpredictkeys.append(keytemp)

                    modelkeytemp = "{} - {} - ({}, {}) {}".format(method, yvars[0][-1], yrange[0], yrange[1], paramgrid[i])
                    cvmodelkeys.append(modelkeytemp)

            for key in cvpredictkeys:
                self.list_amend(self.predictkeys, len(self.predictkeys), key)
                self.data[datakey].df[('predict',key)] = 9999  #Need to fill the data frame with dummy values until CV is actually run

            for n, key in enumerate(cvmodelkeys):
                self.list_amend(self.modelkeys, len(self.modelkeys), key)
                self.modelkeys.append(key)
                self.model_xvars[key] = xvars
                self.model_yvars[key] = yvars
                if method != 'GP':
                    coef = self.data[datakey].df[xvars[0]].columns.values*0.0+9999  #Fill with dummy coeffs before model is run
                    coef = pd.DataFrame(coef)
                    coef.index = pd.MultiIndex.from_tuples(self.data[datakey].df[xvars].columns.values)
                    coef = coef.T
                    coef[('meta', 'Model')] = key
                    try:
                        coef[('meta', 'Intercept')] = 0 #Fill intercept with zeros prior to model run
                    except:
                        pass
                    try:
                        self.data['Model Coefficients'] = spectral_data(
                            pd.concat([self.data['Model Coefficients'].df, coef]))
                    except:
                        self.data['Model Coefficients'] = spectral_data(coef)
                        self.datakeys.append('Model Coefficients')

            self.list_amend(self.datakeys, len(self.datakeys), 'CV Results ' + modelkey)
        except:
            pass


    def run(self):
        method = self.chooseAlgorithmComboBox.currentText()
        datakey = self.chooseDataComboBox.currentText()
        xvars = [str(x.text()) for x in self.xVariableList.selectedItems()]
        yvars = [('comp', str(y.text())) for y in self.yVariableList.selectedItems()]
        yrange = [self.yMinDoubleSpinBox.value(), self.yMaxDoubleSpinBox.value()]
        # Warning: Params passing through cv.cv(params) needs to be in lists
        # Example: {'n_components': [4], 'scale': [False]}
        params, modelkey = self.alg[self.chooseAlgorithmComboBox.currentText()].run()

        #if the method supports it, separate out alpha from the other parameters and prepare for calculating path
        path_methods =  ['Elastic Net', 'LASSO']#, 'Ridge']
        if method in path_methods:
            calc_path = True
            alphas = params.pop('alpha')
        else:
            alphas = None
            calc_path = False
        y = np.array(self.data[datakey].df[yvars])
        match = np.squeeze((y > yrange[0]) & (y < yrange[1]))
        data_for_cv = spectral_data(self.data[datakey].df.ix[match])
        paramgrid = list(ParameterGrid(params))  # create a grid of parameter permutations
        cv_obj = cv.cv(paramgrid)
        try:
            cv_iterator = LeaveOneGroupOut().split(data_for_cv.df[xvars], data_for_cv.df[yvars], data_for_cv.df[
                ('meta', 'Folds')])  # create an iterator for cross validation based on the predefined folds
            n_folds = LeaveOneGroupOut().get_n_splits(groups=data_for_cv.df[('meta', 'Folds')])

        except:
            print('***No folds found! Did you remember to define folds before running cross validation?***')

        self.data[datakey].df, self.cv_results, cvmodels, cvmodelkeys, cvpredictkeys = cv_obj.do_cv(data_for_cv.df, cv_iterator, xcols=xvars,
                                                                                     ycol=yvars, yrange=yrange, method=method,
                                                                                     alphas = alphas, calc_path = calc_path, n_folds = n_folds)
        for key in cvpredictkeys:
            self.list_amend(self.predictkeys, len(self.predictkeys), key)

        for n, key in enumerate(cvmodelkeys):
            self.list_amend(self.modelkeys, len(self.modelkeys), key)
            self.modelkeys.append(key)
            self.models[key] = cvmodels[n]
            self.model_xvars[key] = xvars
            self.model_yvars[key] = yvars
            if method != 'GP':
                coef = np.squeeze(cvmodels[n].model.coef_)
                coef = pd.DataFrame(coef)
                coef.index = pd.MultiIndex.from_tuples(self.data[datakey].df[xvars].columns.values)
                coef = coef.T
                coef[('meta', 'Model')] = key
                try:
                    coef[('meta', 'Intercept')] = cvmodels[n].model.intercept_
                except:
                    pass
                try:
                    self.data['Model Coefficients'] = spectral_data(
                        pd.concat([self.data['Model Coefficients'].df, coef]))
                except:
                    self.data['Model Coefficients'] = spectral_data(coef)
                    self.datakeys.append('Model Coefficients')

        self.datakeys.append('CV Results ' + modelkey)
        self.data['CV Results ' + modelkey] = self.cv_results

    def yvar_choices(self):
        try:
            yvarchoices = self.data[self.chooseDataComboBox.currentText()].df['comp'].columns.values
            yvarchoices = [i for i in yvarchoices if not 'Unnamed' in i]  # remove unnamed columns from choices
        except:
            yvarchoices = ['No composition columns!']
        return yvarchoices

    def xvar_choices(self):
        try:
            xvarchoices = self.data[self.chooseDataComboBox.currentText()].df.columns.levels[0].values
            xvarchoices = [i for i in xvarchoices if not 'Unnamed' in i]  # remove unnamed columns from choices
        except:
            xvarchoices = ['No valid choices!']
        return xvarchoices

    def hideAll(self):
        for a in self.alg:
            self.alg[a].setHidden(True)

    def regressionMethods(self):
        self.alg = {'ARD': cv_ARD.Ui_Form(),
                    'BRR': cv_BayesianRidge.Ui_Form(),
                    'Elastic Net': cv_ElasticNet.Ui_Form(),
                    'GP': cv_GP.Ui_Form(),
                    #'KRR': cv_KRR.Ui_Form(),
                    'LARS': cv_LARS.Ui_Form(),
                    'LASSO': cv_Lasso.Ui_Form(),
                    #'LASSO LARS': cv_LassoLARS.Ui_Form(),
                    'OLS': cv_OLS.Ui_Form(),
                    'OMP': cv_OMP.Ui_Form(),
                    'PLS': cv_PLS.Ui_Form(),
                    'Ridge': cv_Ridge.Ui_Form(),
                    'SVR': cv_SVR.Ui_Form()
                    }

        for item in self.alg:
            self.alg[item].setupUi(self.Form)
            self.algorithmLayout.addWidget(self.alg[item].get_widget())
            self.alg[item].setHidden(True)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = CrossValidation()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
