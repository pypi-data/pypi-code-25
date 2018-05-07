import pandas as pd
import numpy as np
from scipy.stats import t


def _handle_missing_values(x, y):
    """ Remove any observations that have missing values to make sure the
    regression model can be fitted

    TODO: We can have more handle methods such as "use value nearby" or "avg"
    
    Args:
        x (numpy.array): N x K matrix of X observations, where each row is one
            point and each column is a dimension.
        y (numpy.array): 1 x N vector of Y observations.

    Returns:
        tuples: the new x, y with nan values removed and one-to-one matched as
        before.
    """
    x_nan_rows = np.unique(list(map(lambda x: x[0], np.argwhere(np.isnan(x)))))
    y_nan_rows = np.unique(list(map(lambda x: x[0], np.argwhere(np.isnan(y)))))
    remove_rows = np.union1d(x_nan_rows, y_nan_rows)

    return (np.delete(x, remove_rows.astype(int), axis=0), 
            np.delete(y, remove_rows.astype(int), axis=0))





def fit_regression(x, y, intercept=True):
    """Fit a linear regression model.

    TODO: format x, y when they are 1d array

    Args:
        x (numpy.array): N x K matrix of X observations, where each row is one
            point and each column is a dimension.
        y (numpy.array): 1 x N vector of Y observations.
        intercept (bool): Whether the model contains the alpha term, default to
            True.

    Returns:
        numpy.array: 1 dimension vector where the first element is beta_0 and
        the second is beta_1

    Notes:
        For param x, no need to insert one vector as the first column for the
        input. This function will do that.
    """
    # Check if the input variables have missing values, if so, handle them
    if np.isnan(x).any() or np.isnan(y).any():
        x, y = _handle_missing_values(x, y)

    if intercept == True:
        X = np.concatenate((np.repeat(1, len(x)).reshape([-1, 1]), x), axis=1)
    else:
        X = x
    beta = np.linalg.inv(X.T.dot(X)).dot(X.T.dot(y))

    return beta.flatten()


def predict_regression(beta, x, intercept=True):
    """ Predict based on input observations and fitted betas

    Args:
        beta (numpy.array): 1 x K vector of beta params. If there is no alpha,
            the first item should be beta1.
        x (numpy.array): N x K matrix of X observations, where each row is one
            point and each column is a dimension.
        intercept (bool): Whether the model contains the alpha term, default to
            True.

    Returns:
        numpy.array: 1 dimension vector as the predicted value of each obs.
    """
    if intercept == True:
        X = np.concatenate((np.repeat(1, len(x)).reshape([-1, 1]), x), axis=1)
    else:
        X = x
    pred = X.dot(beta)
    return pred.flatten()


def t_test_beta(beta, x, y):
    """ Conduct a T-test to validate the null hypothesis that the beta_i is 0

    #TODO: Intercept case

    Args:
        beta (numpy.array): 1 x K vector of beta params, where first element is
            b0
        x (numpy.array): N x K matrix of X observations, where each row is one
            point and each column is a dimension
        y (numpy.array): 1 x N vector of Y observations

    Returns:
        dict: dict of str:list of float

        {
            "tstat": a list of t-statistics for each beta,
            "p": a list of p-values for each beta,
            "se": a list of standard error for each beta
        }
    """
    # Check if the input variables have missing values, if so, handle them
    if np.isnan(x).any() or np.isnan(y).any():
        x, y = _handle_missing_values(x, y)

    # Add the one vector at the first column of X matrix
    X = np.concatenate((np.repeat(1, len(x)).reshape([-1, 1]), x), axis=1)

    # se for beta_i can be picked from diagonal element of the matrix
    pred = X.dot(beta)
    sigma_error = (pred - y).var()
    sigma_x = np.linalg.inv(X.T.dot(X))
    se_square = sigma_error * sigma_x

    # df is the degree of freedom for T distribution
    df = X.shape[0] - X.shape[1]
    std_e = list(map(lambda i: np.sqrt(se_square[i, i]), range(X.shape[1])))
    tstats = list(map(lambda i: beta[i][0] / std_e[i], range(X.shape[1])))
    pvalues = list(map(lambda tstat: (min(t.cdf(tstat, df),
                                          1 - t.cdf(tstat, df))) * 2, tstats))

    return {"tstat": tstats, "p": pvalues, "se": std_e}


def r_square(beta, x, y):
    """ Caculate the R square score for a linear regression model

    Args:
        beta (numpy.array): a vector of beta parameters
        x (numpy.array): N x K matrix of X observations, where each row is one
            point and each column is a dimension (first column is not 1)
        y (numpy.array): 1 x N vector of Y observations

    Returns:
        float: the R square score for the given model
    """
    # Check if the input variables have missing values, if so, handle them
    if np.isnan(x).any() or np.isnan(y).any():
        x, y = _handle_missing_values(x, y)

    # Add the one vector at the first column of X matrix
    X = np.concatenate((np.repeat(1, len(x)).reshape([-1, 1]), x), axis=1)

    pred = X.dot(beta)
    error = pred - y
    y_diff = y - y.mean()
    return (1 - error.T.dot(error) / y_diff.T.dot(y_diff))[0][0]
