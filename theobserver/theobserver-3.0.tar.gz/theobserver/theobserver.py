import numpy as np

from math import log2
from pandas import read_csv
from sklearn.metrics import silhouette_score


class Observer():
    """Observe and extract information about a dataset.

    Arguments
        filepath: string
            The dataset's absolute/relative path. Must be a CSV format file.

        target_i: {-1, 0}
            The target's column index. The default is -1.

    Return
        An Observer object
    """
    def __init__(self, filepath, target_i=-1):
        self.filepath = filepath
        self.target_i = target_i

    def __sep(self):
        file = open(self.filepath)
        line = file.readline()
        file.close()

        comma = line.count(',')
        semicolon = line.count(';')

        return ',' if comma > semicolon else ';'

    def __data(self, na_values=[]):
        na_values = ['?'] + na_values
        data = read_csv(self.filepath, self.__sep(), header=None, na_values=na_values)
        _, n_columns = data.shape

        # Initial and final column index (exclusive on stop)
        i = self.target_i + 1            # initial
        j = n_columns + self.target_i    # final + 1 (because it's exclusive)

        X = data.iloc[:, i:j]
        y = data.iloc[:, self.target_i]

        return X, y

    def __x(self, na_values=[]):
        X, y = self.__data(na_values)
        return X

    def __y(self, na_values=[]):
        X, y = self.__data(na_values)
        return y

    def n_instances(self):
        """Get the number of instances."""
        file = open(self.filepath)
        i = [1 for line in file]
        file.close()

        return sum(i)

    def n_features(self):
        """Get the number of features."""
        file = open(self.filepath)
        line = file.readline()
        file.close()

        d = self.__sep()

        return len(line.split(d)) - 1

    def n_targets(self):
        """Get the number of targets."""
        d = self.__sep()
        file = open(self.filepath)

        targets = [line.split(d)[self.target_i] for line in file]
        targets = set(targets)

        return len(targets)

    def silhouette(self):
        """Get the mean Silhouette Coefficient for all samples."""
        X = self.__x()
        y = self.__y()

        return silhouette_score(X, y)

    def entropy(self):
        """Get the samples' entropy."""
        y = self.__y()
        sety, counts = np.unique(y, return_counts=True)
        total = len(y)

        result = 0
        for target, n in zip(sety, counts):
            p = n / total
            result = result - (p * log2(p))

        return result

    def unbalanced(self):
        """Get the unbalaced metric, where 1 is very balanced and 0 extremely unbalaced."""
        sety = set(self.__y())
        n = len(sety)

        return self.entropy() / log2(n)

    def n_binary_features(self):
        """Get the number of binary features, i.e., features with only 2 labels."""
        x = self.__x()
        m, n = x.shape

        bin_features = [len(set(x.iloc[:, j])) == 2 for j in range(n)]

        return sum(bin_features)

    def majority_class_size(self):
        """Get the number of instances labeled with the most frequent class."""
        y = self.__y()
        sety, counts = np.unique(y, return_counts=True)

        return np.max(counts)

    def minority_class_size(self):
        """Get the number of instances labeled with the least frequent class."""
        y = self.__y()
        sety, counts = np.unique(y, return_counts=True)

        return np.min(counts)

    def features_with_na(self, na_values=[]):
        """Get the number of features with missing values.

        Arguments:
            na_values: list (default [])
                a list of strings or ints to interpret as NaN values.
        """
        X = self.__x(na_values)
        X_na = X.isnull().any()

        return X_na.sum()

    def missing_values(self, na_values=[]):
        """Get the number of missing values.

        Arguments:
            na_values: list (default [])
                a list of strings or ints to interpret as NaN values.
        """
        X = self.__x(na_values)
        y = self.__y(na_values)

        X_na = X.isnull()
        y_na = y.isnull()

        X_na_sum = X_na.sum().sum()
        y_na_sum = y_na.sum().sum()

        return X_na_sum + y_na_sum

    def extract(self):
        """Extract all the observed information.

        Return
            [n_instances,
             n_features,
             n_targets,
             silhouette,
             unbalanced,
             n_binary_features,
             majority_class_size,
             minority_class_size,
             features_with_na,
             missing_values]
        """
        ins = self.n_instances()
        fea = self.n_features()
        tar = self.n_targets()
        sil = self.silhouette()
        unb = self.unbalanced()
        nbi = self.n_binary_features()
        maj = self.majority_class_size()
        mio = self.minority_class_size()
        fna = self.features_with_na()
        nav = self.missing_values()

        return [ins, fea, tar, sil, unb, nbi, maj, mio, fna, nav]

