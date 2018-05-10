import numpy
import statsmodels.tsa.stattools as statsmodels_stattools


def run_test(data):
    X = numpy.log(data.values)
    adf = statsmodels_stattools.adfuller(X)
    message = '\nADF Statistic: {:.4}, p-value: {:.4}, Significance Level: 1%\n'.format(adf[0], adf[1])

    if adf[4]['1%'] > adf[0]:
        message += 'Reject the null hypothesis: the series is stationary.'
        stationary = True

    else:
        message += 'Accept the null hypothesis: the series is not stationary.'
        stationary = False

    adf_data = {'result': 'info', 'message': message, 'stationary': stationary}

    return adf_data