import random
import numpy as np
from collections import Counter
from sklearn.tree import DecisionTreeClassifier
from sklearn.decomposition import PCA


class RotationForest:
    def __init__(self, n_trees=10,
                 bagging=True,
                 warm=False, **kwargs):
        self.n_trees = n_trees
        self.trees = None
        self.warm = warm  # TODO
        self.bagging = bagging  # TODO

        if 'max_features' not in kwargs:
            kwargs['max_features'] = 'auto'
        self.kwargs = kwargs
        self.trees = None
        self.rotations = None
        self.x, self.y = None, None

    def __fit_tree(self, *a, **kw):
        x, y = self.x, self.y
        assert x is not None
        assert y is not None
        y_len = len(y)
        if self.bagging:
            n = int(len(y) / 3)
            ind = [random.choice(range(y_len))
                   for _ in range(n)]
            x, y = x.take(ind, axis=0), y.take(ind, axis=0)
            pca = PCA()
            x = pca.fit_transform(x)
            tree = DecisionTreeClassifier(**self.kwargs)
            tree.fit(x, y)
        return tree, pca

    def __predict_tree(self, args):
        (tree, rotation), x = args, self.x
        assert x is not None
        x = rotation.transform(x)
        y = tree.predict(x)
        return y

    def fit(self, x, y):
        if self.warm or (not self.warm and self.trees is None):
            self.trees, self.rotations = [], []
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)
        assert len(x.shape) == 2
        assert len(y.shape) == 1
        self.x, self.y = x, y
        # TODO: Parallelize
        mapper = map(self.__fit_tree, [tuple() for _ in range(self.n_trees)])
        for tree, rotation in mapper:
            self.trees.append(tree)
            self.rotations.append(rotation)
        return self

    def predict(self, x):
        self.x = x
        mapper = map(self.__predict_tree,
                     zip(self.trees, self.rotations))
        y = None
        for y_ in mapper:
            if y is None:
                y = [Counter([i]) for i in y_]
            else:
                for count, i in zip(y, y_):
                    count.update({i: 1})
        y = [count.most_common(1)[0][0]
             for count in y]
        return y
