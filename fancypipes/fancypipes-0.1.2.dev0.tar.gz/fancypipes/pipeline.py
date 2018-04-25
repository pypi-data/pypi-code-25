import collections
from sklearn import pipeline
import pandas as pd
from sklearn.model_selection import KFold

from .scorers import _classifier_scores, _regression_scores


def _get_pipeline_type(name):
    classifiers = ['LogisticRegression', 'RandomForestClassifier']
    regressors = ['RandomForestRegressor', 'Lasso', 'Ridge']

    if name in classifiers:
        return 'classifier'
    elif name in regressors:
        return 'regressor'
    else:
        raise AttributeError()


def _is_regressor(pipeline_type):
    return True if pipeline_type == 'regressor' else False


def _is_classifier(pipeline_type):
    return True if pipeline_type == 'classifier' else False


def _get_scoring_method(pipeline_type):
    if pipeline_type == 'classifier':
        return _classifier_scores
    elif pipeline_type == 'regressor':
        return _regression_scores
    else:
        raise AttributeError()


def _check_pipeline_is_prepped(evaluator):
    if evaluator.prep_steps_fitted:
        pass
    else:
        raise ValueError("Pipeline has not yet been prepped")


def _get_X(X, columns=None, inplace=True):
    if columns is None:
        columns = X.columns
    if inplace:
        return X.loc[:, columns]
    else:
        return X.loc[:, columns].copy()


def _get_included_column_names(X, ignores):
    columns = X.columns.values

    if len(ignores) == 0:
        return columns

    types = [type(elem) for elem in ignores]
    assert len(set(types)) == 1

    if not isinstance(columns[0], collections.Iterable):      # Column Names
        return list(set(columns) - set(ignores))
    elif types[0] == tuple:                                   # multi-index column names
        return list(set(columns) - set(ignores))
    elif types[0] == list:                                    # Attribute list for multi-index
        return [col for col in columns
                if not any(all(ignore_attr in col for ignore_attr in ignore) for ignore in ignores)]


def _group_applier(grp, model, y, *args, **kwargs):
    return model.evaluate_performance(grp, y[grp.index], *args, **kwargs)


class pipeline(pipeline.Pipeline):
    def __init__(self, steps, ignore_columns=[], diagnostic_package=None):

        super().__init__(steps=steps)
        self._pipeline_type = None
        self._scorer = None
        self._diagnostic_package = diagnostic_package
        self.ignore_columns = ignore_columns

        self.included_columns = []
        self.final_column_names = []
        self._prep_steps_fitted = False

    @property
    def prep_steps_fitted(self):
        return self._prep_steps_fitted

    @prep_steps_fitted.setter
    def prep_steps_fitted(self, value):
        if value not in set([True, False]):
            raise ValueError()
        self._prep_steps_fitted = value

    @property
    def pipeline_type(self):
        model_name = type(self.steps[-1][1]).__name__
        return _get_pipeline_type(model_name)

    @property
    def scorer(self):
        return _get_scoring_method(self.pipeline_type)

    @property
    def diagnostic_package(self):
        if self._diagnostic_package is None:
            self._diagnostic_package = self.scorer
        return self._diagnostic_package

    def _get_X(self, X, inplace=True):
        return _get_X(X, self.included_columns, inplace=inplace)

    def prep_pipeline(self, X, y):
        if self.prep_steps_fitted:
            return

        self.included_columns = _get_included_column_names(X, self.ignore_columns)
        X_temp = self._get_X(X, inplace=False)
        for step in self.steps[:-1]:
            step[-1].fit(X_temp)
            X_temp = step[-1].transform(X_temp)

        self.final_column_names = X_temp.columns.values.tolist()
        self.prep_steps_fitted = True

    def transform_data(self, X, inplace=False):
        _check_pipeline_is_prepped(self)

        X_temp = self._get_X(X, inplace=inplace)
        for step in self.steps[:-1]:
            X_temp = step[-1].transform(X_temp)
        return(X_temp)

    def evaluate_performance(self, X, y, by=[], *args, **kwargs):
        if by:
            by = by if isinstance(by, list) else [by]
            extra_column = 'level_{}'.format(str(len(by)))
            ret = X.reset_index(drop=True).groupby(by).apply(_group_applier, self, y, *args, **kwargs)
            return ret.reset_index().drop(columns=extra_column, axis=1)
        else:
            return self.diagnostic_package(self, X, y, *args, **kwargs)

    def fit(self, X, y, inplace=True):
        _check_pipeline_is_prepped(self)
        X = self._get_X(X, inplace=inplace)
        super().fit(X, y)

    def predict(self, X):
        X = self._get_X(X, inplace=True)
        return super().predict(X)

    def predict_proba(self, X):
        X = self._get_X(X, inplace=True)
        return super().predict_proba(X)

    def evaluate_k_folds(self, X, y, k=5, by=[], random_state=42, shuffle=True):
        kf = KFold(k, shuffle, random_state)
        diagnostics_list = []
        for fold, indices in enumerate(kf.split(X)):
            train_index, test_index = indices

            X_train, X_test = X.iloc[train_index, :], X.iloc[test_index, :]
            y_train, y_test = y[train_index], y[test_index]

            self.fit(X_train, y_train)
            results = self.evaluate_performance(X_test, y_test, by=by)
            results['fold'] = fold + 1
            diagnostics_list.append(results)

        result = pd.concat(diagnostics_list)
        if by:
            res2 = result.groupby(by).mean().reset_index()
            res2['fold'] = 'mean'
            result = pd.concat([res2, result])

        result.reset_index(drop=True, inplace=True)
        cols = result.columns.values.tolist()
        cols = cols[-1:] + cols[:-1]
        return result[cols]

    def get_model_coefficients(self):
        if hasattr(self.steps[-1][1], 'densify'):
            self.steps[-1][1].densify()

        if hasattr(self.steps[-1][1], 'coef_'):
            feature_vals = self.steps[-1][1].coef_.T
        elif hasattr(self.steps[-1][1], 'feature_importances_'):
            feature_vals = self.steps[-1][1].feature_importances_

        ret = dict(zip(self.final_column_names, feature_vals))
        ret = {k: v[0] if isinstance(v, collections.Iterable) and len(v) == 1 else v for k, v in ret.items()}

        return ret
