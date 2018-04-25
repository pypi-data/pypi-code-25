import sklearn.metrics as metrics
import numpy as np
import pandas as pd


def absolute_percent_error(y, y_pred):
    return abs(np.divide((y - y_pred), y))


def calculate_aic(y, y_pred, k):
    # http://avesbiodiv.mncn.csic.es/estadistica/ejemploaic.pdf
    n = len(y)
    RSS = sum((y - y_pred)**2)
    aic = n * np.log(RSS / n) + 2 * k
    return aic


def _regression_scores(model, X, y):
    y_pred = model.predict(X)
    n_predictors = len(X.columns)
    record_count = len(y)

    mae = metrics.mean_absolute_error(y, y_pred)
    medae = metrics.median_absolute_error(y, y_pred)
    rmse = np.sqrt(metrics.mean_squared_error(y, y_pred))

    abs_p_e = absolute_percent_error(y, y_pred) if 0 not in y else None
    mape = np.mean(abs_p_e) if abs_p_e is not None else np.nan
    mdape = np.median(abs_p_e) if abs_p_e is not None else np.nan

    aic = calculate_aic(y, y_pred, n_predictors) if n_predictors else np.nan
    r2 = metrics.r2_score(y, y_pred)

    results = {"MAE": mae, "MdAE": medae, "RMSE": rmse, "MAPE": mape,
               "MdAPE": mdape, "R^2 Score": r2, 'AIC': aic,
               'record_count': record_count}

    results = pd.DataFrame.from_records([results])
    return(results)


def _classifier_scores(model, X, y):
    y_pred = model.predict(X)
    y_pred_proba = model.predict_proba(X)
    record_count = len(y)

    accuracy = metrics.accuracy_score(y, y_pred)

    F1 = metrics.f1_score(y, y_pred)
    precision = metrics.precision_score(y, y_pred)
    recall = metrics.recall_score(y, y_pred)

    roc_auc = metrics.roc_auc_score(y, y_pred_proba)
    log_loss = metrics.log_loss(y, y_pred_proba)

    matthews_corrcoef = metrics.matthews_corrcoef(y, y_pred)

    results = {'Accuracy': accuracy, 'Precision': precision, 'Recall': recall, 'F1': F1,
               'ROC-AUC': roc_auc, 'log-loss': log_loss, 'Matt Corrcoeff': matthews_corrcoef,
               'record_count': record_count}

    results = pd.DataFrame.from_records([results])
    return(results)
