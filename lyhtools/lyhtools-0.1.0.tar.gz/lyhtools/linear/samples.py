from scipy.stats import f
from scipy.stats import t


def f_stat(s1, s2):
    """ Given two samples, return the F-test value and its p-value

    Args:
        s1 (numpy.array): 1d array for the sample 1
        s2 (numpy.array: 1d array for the sample 1

    Returns:
        dict: dict of str:list of float

        {
            'fstat': the F-statistic,
            'p': the P-value of the given statistic
        }
    """
    var1 = s1.var()
    var2 = s2.var()
    if var1 > var2:
        return {
            'fstat': var1/var2,
            'p': 1-f.cdf(var1/var2, len(s1)-1, len(s2)-2)
        }
    else:
        return {
            'fstat': var2/var1,
            'p': 1-f.cdf(var2/var1, len(s2)-1, len(s1)-2)
        }


def t_stat(s1, s2):
    """ Given two samples, return the T-test value and its p-value
    TODO: This is only for variance different case, may need to implement variance equal test

    Args:
        s1 (numpy.array): 1d array for the sample 1
        s2 (numpy.array: 1d array for the sample 1

    Returns:
        dict: dict of str:list of float

        {
            'tstat': the T-statistic,
            'p': the P-value of the given statistic
        }
    """
    u1 = s1.mean()
    u2 = s2.mean()
    var1 = s1.var()
    var2 = s2.var()

    ts = (u1 - u2) / (var1 / len(s1) + var2 / len(s2)) ** 0.5
    p = min(t.cdf(ts, len(s1) + len(s2) - 2),
            1 - t.cdf(ts, len(s1) + len(s2) - 2))
    return {'tstat': ts, 'p': p}
