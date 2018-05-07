"""
In this module, we will set up and validate several capm related theories and
trading strategies.
"""
import numpy as np
import pandas as pd
from lyhtools.linear.regression import fit_regression


def rebalance(x, y, n):
    """ Re-balance the current portfolio based on betting against beta strategy.

    The idea is to fit a regression model based on the factor matrix and the
    given return matrix. Each factor's beta will be used to weight the
    portfolio. The n largest and smallest beta will be picked. The beta exceeds
    the average most will be shorted with largest weight, and the beta
    under-performs the average most will be longed with largest weight.

    Args:
        x (numpy.array): N x K matrix of X observations, where each row is one
            point and each column is a dimension. In this case, we want each
            row to be one trading time, T, and each column to be one feature or
            factor. The observation would be the "factor" value at that point.

        y (pandas.DataFrame): N x M df of Y observations. Normally a return or
            log-excess-return (excess). The columns represent different stocks
            and rows are different time-beings.

        n (int): The number of stocks to be picked at the top and bottom.

    Returns:
        pandas.Sieres: 2n stocks will be selected in the portfolio with their
        normalized weights.
    """

    # Fit betas for each stock
    beta_m = []
    for i in range(y.shape[1]):
        beta_m.append(fit_regression(x, y.values[:, i]).reshape([1, -1]))
    beta_m = np.concatenate(beta_m)

    # When calculating the average beta, we will ignore the alpha term,
    # since by CAPM assumption, those alphas should be 0
    beta_avg_m = beta_m[:, 1:].mean(axis=1)

    top_n = beta_avg_m.argsort()[-n:]
    bottom_n = beta_avg_m.argsort()[:n]

    # Select the top and bottom n stocks
    selected_beta = pd.Series(beta_avg_m[np.concatenate((top_n, bottom_n))],
                              index=y.columns[np.concatenate((top_n,
                                                              bottom_n))])

    selected_beta = selected_beta - selected_beta.mean()

    return -selected_beta/selected_beta.sum()


def bab_simulate(x, y, t0, n):
    """ Using the betting against beta strategy to simulate the portfolio's
    performance based on historical stocks' returns.

    Args:
        x (numpy.array): N x K matrix of X observations, where each row is one
            point and each column is a dimension. In this case, we want each
            row to be one trading time, T, and each column to be one feature or
            factor. The observation would be the "factor" value at that point.

        y (pandas.DataFrame): N x M df of Y observations. Normally a return or
            log-excess-return (excess). The columns represent different stocks
            and rows are different time-beings.

        t0 (int): The simulation will start at t0 point of the historical data.
            The first set of weights will be generated based on data of t0 - 1.

        n (int): The number of stocks to be picked at the top and bottom.

    Returns:
        pandas.Series: A set of portfolio returns on each date.
    """
    returns = []
    # For each time point, we use historical data to re-balance weights, and
    # calculate portfolio return at that time point based on market returns
    # on that point.
    for t in range(t0, y.shape[0]):
        x_past = x[:t - 1, ]
        y_past = y.iloc[:t - 1, ]
        returns.append((y.iloc[t, ] * rebalance(x_past, y_past, n)).sum())

    return pd.Series(returns, index=y.index[t0:])
