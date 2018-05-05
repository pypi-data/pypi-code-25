import os
import warnings
import numpy as np

import vaex
import vaex.dataset
from vaex.utils import InnerNamespace

from .pipeline import Pipeline
from .transformations import PCA, StandardScaler, MinMaxScaler


def iris():
    dirname = os.path.dirname(__file__)
    return vaex.open(os.path.join(dirname, 'iris.hdf5'))

def _iris(name, iris_previous, N):
    filename = os.path.join(vaex.utils.get_private_dir('data'), name + '.hdf5')
    if os.path.exists(filename):
        return vaex.open(filename)
    else:
        iris = iris_previous()
        repeat = int(np.ceil(N / len(iris)))
        ds = vaex.dataset.DatasetConcatenated([iris] * repeat)
        ds.export_hdf5(filename)
        return vaex.open(filename)

def iris_1e4():
    '''Returns the iris set repeated so it include ~1e4 rows'''
    return _iris('iris_1e4', iris, int(1e4))

def iris_1e5():
    '''Returns the iris set repeated so it include ~1e5 rows'''
    return _iris('iris_1e5', iris_1e4, int(1e5))

def iris_1e6():
    '''Returns the iris set repeated so it include ~1e6 rows'''
    return _iris('iris_1e6', iris_1e5, int(1e6))

def iris_1e7():
    '''Returns the iris set repeated so it include ~1e7 rows'''
    return _iris('iris_1e7', iris_1e6, int(1e7))

def iris_1e8():
    '''Returns the iris set repeated so it include ~1e8 rows'''
    return _iris('iris_1e8', iris_1e7, int(1e8))

def iris_1e9():
    '''Returns the iris set repeated so it include ~1e8 rows'''
    return _iris('iris_1e9', iris_1e8, int(1e9))

def pca(self, n_components=2, features=None, progress=False):
    '''Requires vaex.ml: Create :class:`vaex.ml.transformations.PCA` and fit it'''
    features = features or self.get_column_names()
    features = vaex.dataset._ensure_strings_from_expressions(features)
    pca = PCA(n_components=n_components, features=features)
    pca.fit(self, progress=progress)
    return pca


def standard_scaler(self, features=None, with_mean=True, with_std=True):
    '''Requires vaex.ml: Create :class:`vaex.ml.transformations.StandardScaler` and fit it'''
    features = features or self.get_column_names()
    features = vaex.dataset._ensure_strings_from_expressions(features)
    standard_scaler = StandardScaler(features=features, with_mean=with_mean, with_std=with_std)
    standard_scaler.fit(self)
    return standard_scaler


def minmax_scaler(self, features=None, feature_range=[0, 1]):
    '''Requires vaex.ml: Create :class:`vaex.ml.transformations.MinMaxScaler` and fit it'''
    features = features or self.get_column_names()
    features = vaex.dataset._ensure_strings_from_expressions(features)
    minmax_scaler = MinMaxScaler(features=features, feature_range=feature_range)
    minmax_scaler.fit(self)
    return minmax_scaler


def xgboost_model(self, label, num_round, features=None, copy=False, param={}):
    '''Requires vaex.ml: create a XGBoost model and train/fit it.

    :param label: label to train/fit on
    :param num_round: number of rounds
    :param features: list of features to train on
    :param bool copy: Copy data or use the modified xgboost library for efficient transfer
    :return vaex.ml.xgboost.XGBModel: fitted XGBoost model
    '''
    from .xgboost import XGBModel
    dataset = self
    features = features or self.get_column_names()
    features = vaex.dataset._ensure_strings_from_expressions(features)
    xg = XGBModel(num_round=num_round, features=features, param=param)
    xg.fit(dataset, label, copy=copy)
    return xg

def lightgbm_model(self, label, num_round, features=None, copy=False, param={}, classifier=False):
    '''Requires vaex.ml: create a lightgbm model and train/fit it.

    :param label: label to train/fit on
    :param num_round: number of rounds
    :param features: list of features to train on
    :param bool copy: Copy data or use the modified xgboost library for efficient transfer
    :param bool classifier: If true, return a the classifier (will use argmax on the probabilities)
    :return vaex.ml.lightgbm.LightGBMModel or vaex.ml.lightgbm.LightGBMClassifier: fitted LightGBM model
    '''
    from .lightgbm import LightGBMModel, LightGBMClassifier
    dataset = self
    features = features or self.get_column_names()
    features = vaex.dataset._ensure_strings_from_expressions(features)
    cls = LightGBMClassifier if classifier else LightGBMModel
    b = cls(num_round=num_round, features=features, param=param)
    b.fit(dataset, label, copy=copy)
    return b


def state_transfer(self):
    from .transformations import StateTransfer
    return StateTransfer(state=self.state_get())

@vaex.dataset.docsubst
def one_hot_encoding(self, expression, prefix=None, numeric=True, zero=None, one=None):
    '''Requires vaex.ml: Turn expression into N columns, for each unique values

    Example:

    >>> color = np.array(['red', 'green', 'blue', 'green'])
    >>> ds = vaex.from_arrays(color=color)
    >>> ds.ml.one_hot_encoding('color')
    >>> assert ds.evaluate('color_red').tolist() == [1, 0, 0, 0]
    >>> assert ds.evaluate('color_green').tolist() == [0, 1, 0, 1]
    >>> assert ds.evaluate('color_blue').tolist() == [0, 0, 1, 0]

    :param expression: {expression}
    :param str prefix: prefix to use in from of all new column names
    :param bool numeric: Use True/False or 1/0 for the values
    :param zero: What value to use for a zero (overrides numeric argument)
    :param one: Similar to zero

    '''
    expression = vaex.dataset._ensure_strings_from_expressions(expression)
    prefix = prefix or expression
    uniques = self.unique(expression)
    uniques = np.sort(uniques)  # gives consistent results

    if numeric:
        if zero is None:
            zero = 0
        if one is None:
            one = 1
    else:
        if zero is None:
            zero = False
        if one is None:
            one = True
    # add a virtual column for each unique value
    for value in uniques:
        column_name = prefix + "_" + str(value)
        self.add_virtual_column(column_name, 'where({expression} == {value}, {one}, {zero})'.format(
            expression=expression, value=repr(value), one=one, zero=zero))


def train_test_split(self, test_size=0.2, strings=True, virtual=True):
    """Will split the dataset in train and test part, assuming it is shuffled.
    """
    warnings.warn('make sure the dataset is shuffled')
    initial = None
    try:
        assert self.filtered is False, 'filtered dataset not supported yet'
        # full_length = len(self)
        self = self.trim()
        initial = self.get_active_range()
        self.set_active_fraction(test_size)
        test = self.trim()
        __, end = self.get_active_range()
        self.set_active_range(end, self.length_original())
        train = self.trim()
    finally:
        if initial is not None:
            self.set_active_range(*initial)
    return train, test


def add_namespace():
    vaex.dataset.Dataset.ml = InnerNamespace({}, vaex.dataset.Dataset, prefix='ml_')
    # try:
    #     from . import generated
    # except ImportError:
    #     print("importing generated code failed")
    vaex.dataset.Dataset.ml._add(train_test_split=train_test_split)

    def to_xgboost_dmatrix(self, label, features=None, selection=None, blocksize=1000 * 1000):
        """

        label: ndarray containing the labels
        """
        from . import xgboost
        return xgboost.VaexDMatrix(self, label, features=features, selection=selection, blocksize=blocksize)

    vaex.dataset.Dataset.ml._add(to_xgboost_dmatrix=to_xgboost_dmatrix, xgboost_model=xgboost_model,
                                 lightgbm_model=lightgbm_model,
                                 state_transfer=state_transfer,
                                 one_hot_encoding=one_hot_encoding,
                                 pca=pca,
                                 standard_scaler=standard_scaler,
                                 minmax_scaler=minmax_scaler)
    del to_xgboost_dmatrix

    # named_objects.update({ep.name: ep.load()})
