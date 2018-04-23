'''
    Mindstrong biomarker model fitting software, cross-validation model
    fitting functions.
    Copyright (C) 2018  Mindstrong Health, Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import numpy as np
import pandas as pd
import numpy.matlib
from sklearn import linear_model, preprocessing
from sklearn.model_selection import LeaveOneOut, KFold, LeaveOneGroupOut, GroupKFold
from scipy import linalg
from scipy.stats import stats
import sys, os


def calculateCrossValidatedCorrelation(target_df, feature_df, target_colname, fold_type, n_folds,
                                       correlation_function_name='pearsonr', regularization=0.1,
                                       kernel_training='linear', kernel_training_param=1,
                                       kernel_target='linear', kernel_target_param=1):
    """
    This function calculates the cross_validated correlation for each test target
    across a range of eigenvector selections.

    :param target_df: data frame of target measures
    :param best_features: dict of data frames of biomarker features, one for each test
    :param fold_type: 'subject' or 'observation'
    :param n_folds: if an integer, specifies the number of folds. Otherwise will do leave-one-out.
    :param correlation_function_name: pearsonr, spearmanr, kendalltau
    :param kernelTraining: The selected training kernel for the kernel supervised PCA dimension reduction technique.
    :param kernelTrainingParam: Training kernel parameter passed to GenerateTrainingModel.
    :param kernelTarget: The selected target kernel for the kernel supervised PCA dimension reduction technique.
    :param kernelTargetParam: Target kernel parameter passed to GenerateTrainingModel.
    :return: crossValidatedDF, a pandas dataframe with rows consisting of a test and eigenvector space size,
    and columns consisting of various statistical information such as the cross-validated correlation, and its
    associated p-value.
    """

    cvdf_column_names = ["test", "parameter", "correlation", "p_value", "rows", "features", "subjects", "fold_type", "n_folds"]
    cvdf = pd.DataFrame(columns=cvdf_column_names)
    predictions = {}
    corrfn = getattr(stats, correlation_function_name)

    labels = feature_df.index.get_level_values(0)
    features = feature_df.values
    target = target_df.values
    na = np.isnan(target).flatten()
    features = features[~na, :]
    target = target[~na]
    folds, n_used_params = generateFoldsAndParams(labels[~na], fold_type, n_folds)
    standardizedTarget = centerFeatureMatrix(np.array(target), True, mu_vector=None, sd_vector=None)[0][:, 0]

    if folds:
        for param in range(n_used_params):
            progress(param, n_used_params, target_colname)
            predictions = calculateCrossValidatedPrediction(features, target, folds, regularization,
                          kernel_training, kernel_training_param,
                          kernel_target, kernel_target_param, param)

            cvdf = cvdf.append(pd.DataFrame([[target_colname, param + 1,
                corrfn(standardizedTarget, predictions)[0],
                corrfn(standardizedTarget, predictions)[1],
                features.shape[0], features.shape[1], len(set(labels)), fold_type, n_folds]
            ], columns=cvdf_column_names), ignore_index=True)

    best_model = cvdf.groupby("test", as_index=False, sort=False).apply(lastIncreasing).\
        reset_index()[cvdf_column_names]

    return cvdf, best_model


def ComputeKernelV2(Ztest, Ztrain, kerneltype, kernelparam):
    # if Ztest is mxp, Ztrain is nxp, then kernel is mxn
    a = np.diagonal(np.dot(Ztest, Ztest.T))  # length m
    b = np.diagonal(np.dot(Ztrain, Ztrain.T))  # length n
    A = np.matlib.repmat(a.reshape(len(a), 1), 1, len(b))  # mxn
    B = np.matlib.repmat(b, len(a), 1)  # mxn
    arg = abs(A + B - 2 * np.dot(Ztest, Ztrain.T))
    if kerneltype == 'radial':
        kernel = np.exp(-arg / kernelparam)
    elif kerneltype == 'laplace':
        kernel = np.exp(-np.sqrt(arg) / kernelparam)
    elif kerneltype == 'exponential':
        kernel = np.exp(-(np.dot(Ztest, Ztrain.T)) / kernelparam)
    elif kerneltype == 'linear':
        kernel = np.dot(Ztest, Ztrain.T)
    elif kerneltype == 'polynomial':
        kernel = np.power( (1 + np.dot(Ztest, Ztrain.T)), kernelparam)
    elif kerneltype == 'power':
        kernel = - np.power(arg, kernelparam)
    elif kerneltype == 'log':
        kernel = - np.log(1.0 + np.power(arg, kernelparam))
    return kernel


def generateTestModel(X, testX, kernelX, kernelXParam, kernelCenteringObject):
    centeredX, mu_vector, sd_vector = centerFeatureMatrix(X, True, None, None)
    centeredTestX, mu_vector, sd_vector = centerFeatureMatrix(testX, False, mu_vector, sd_vector)
    kernelResult = ComputeKernelV2(centeredTestX, centeredX, kernelX, kernelXParam)
    kernelResultCentered = kernelCenteringObject.transform(kernelResult)
    return kernelResultCentered


def generateTrainingModel(X, kernelX, kernelXParam, T, kernelT, kernelTParam, regularization):
    # centers across the rows as matrices are nxp.
    centeredX, mu_vector, sd_vector = centerFeatureMatrix(X, True, mu_vector=None, sd_vector=None)
    centeredT, mu_vector, sd_vector = centerFeatureMatrix(T, True, mu_vector=None, sd_vector=None)
    kernelResult = ComputeKernelV2(centeredX, centeredX, kernelX, kernelXParam)
    centeringK = preprocessing.KernelCenterer()
    centeringK = centeringK.fit(kernelResult)
    kCentered = centeringK.transform(kernelResult)
    Lambda = regularization * max(np.diag(kCentered))
    kCentered = (kCentered + Lambda * np.eye(kCentered.shape[0]))
    L = ComputeKernelV2(centeredT, centeredT, kernelT, kernelTParam)
    Q = np.dot(kCentered, np.dot(L, kCentered))
    D, V = linalg.eigh(Q, kCentered)
    D[np.isinf(D)] = 0
    oidx = sorted(range(len(D)), key=lambda i: -abs(D[i].real))
    V = V[:, oidx]
    return kCentered, V.real, Q, L, D[oidx], centeringK, centeredT


def predict(K, Ktest, selectedEigenvectors, targetVector):
    trainedKernelPredictors = np.dot(K, selectedEigenvectors)
    newDataKernelPredictors = np.dot(Ktest, selectedEigenvectors)
    linearRegressionModel = linear_model.LinearRegression().fit(trainedKernelPredictors, targetVector)
    predictedValues = linearRegressionModel.predict(newDataKernelPredictors)
    return linearRegressionModel, predictedValues


def centerFeatureMatrix(featureMatrix, calculateCenter, mu_vector, sd_vector):
    if(calculateCenter):
        if featureMatrix.ndim == 1:
            featureMatrix = featureMatrix.reshape(len(featureMatrix),1)
        (nrow, ncol) = featureMatrix.shape
        mu_vector = np.mean(featureMatrix, axis=0)
        Z = featureMatrix - np.matlib.repmat(mu_vector, nrow, 1)
        sd_vector = np.empty([0])
        for j in range(ncol):
            sd_vector = np.append(sd_vector, np.std(Z[:, j], ddof=1, dtype=np.float64))
            if sd_vector[j] == float(0):
                sd_vector[j] = 1
            Z[:, j] = Z[:, j] / sd_vector[j]
    else:
        (nrow, ncol) = featureMatrix.shape
        Z = featureMatrix - np.matlib.repmat(mu_vector, nrow, 1)
        for j in range(ncol):
            if sd_vector[j] == float(0):
                sd_vector[j] = 1
            Z[:, j] = Z[:,j] / sd_vector[j]
    return Z, mu_vector, sd_vector


def generateFoldsAndParams(labels, fold_type, n_folds):
    if fold_type == "observation":
        if n_folds == "loo":
            folds = list(LeaveOneOut().split(labels))
        else:
            folds = list(KFold(n_splits=n_folds).split(labels))
    else:
        if n_folds == "loo":
            try:
                folds = list(LeaveOneGroupOut().split(labels, labels, labels))
            except ValueError:
                folds = None
        else:
            try:
                folds = list(GroupKFold(n_splits=n_folds).split(labels, labels, labels))
            except ValueError:
                folds = None
    if folds:
        max_left_out = max([len(test) for train, test in folds])
        n_used_params = min(len(labels) - max_left_out, 15)
    else:
        n_used_params = None
    return folds, n_used_params


def calculateCrossValidatedPrediction(features, target, folds, regularization,
                                      kernel_training, kernel_training_param,
                                      kernel_target, kernel_target_param, param):
    predictions = np.zeros(features.shape[0])
    for train_IDs, test_IDs in folds:
        K, V, Q, L, D, kernel_centering_object, centered_T = generateTrainingModel(
            features[train_IDs, :], kernel_training, kernel_training_param, target[train_IDs],
            kernel_target, kernel_target_param, regularization)
        Ktest = generateTestModel(features[train_IDs, :], features[test_IDs, :],
                                  kernel_training, kernel_training_param, kernel_centering_object)
        regressionModelSciKit, predictedTarget = predict(K, Ktest, V[:, range(param + 1)], centered_T)
        predictions[test_IDs] = predictedTarget[:, 0]
    return predictions


def lastIncreasing(cross_validated_correlations):
    """
    Calculate the best cross-validated correlation with a sparsity tradeoff.
    """
    increasing = np.flatnonzero(np.diff(cross_validated_correlations.correlation.values) < 0)
    if len(increasing):
        return cross_validated_correlations.iloc[increasing[0]]
    else:
        return cross_validated_correlations.iloc[-1]


def progress(count, total, status=''):
    # courtesy https://gist.github.com/VincentLoy/73d42c84811fed67cc38
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percent = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write("[%s] %0.1f%%   %s                              \r" % (bar, percent, status))
    sys.stdout.flush()


def get_example_data(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', path)


