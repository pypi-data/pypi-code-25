import numpy as np
from pymaniprob.probabilitydistributions import MultivariateProbabilityDistribution
from scipy.special import hyp1f1

class BaseWatson(MultivariateProbabilityDistribution):
    def __init__(self, m, k, p, **kwargs):
        self.m = m
        self.k = k
        self.p = p
        super(BaseWatson, self).__init__(dim=p, **kwargs)


class FrozenWatson(BaseWatson):

    def __init__(self, m, k, p):

        self.norm_const = 1/hyp1f1(0.5, p/2, k)
        self.log_norm_const = np.log(self.norm_const)

        def _pdf(x):
            exp_arg = self.k*np.dot(self.m, x)**2
            return np.exp(exp_arg)*self.norm_const

        def _logpdf(x):
            exp_arg = self.k*np.dot(self.m, x)**2
            return exp_arg + self.log_norm_const

        super(FrozeWatson, self).__init__(m=m, k=k, p=p,
                                          _pdf=_pdf,
                                          _logpdf=_logpdf)

class Watson:

    def __new__(self, m=None, k=1, p=2):
        m, k, p = _handle_parameter_specification(m, k, p)
        return FrozenWatson(m=m, k=k, p=p)


    @classmethod
    def pdf(self, x, m=None, k=None, p=None, normalised=True):

        # the unnormalised watson density function
        def _updf(x):
            return np.exp(k*np.dot(m, x)**2)

        if normalised:
            norm_const = 1/hyp1f1(0.5, p/2, k)
            return _updf(x)*norm_const

        else:
            return _updf(x)


"""
Utility methods for setting up
"""
def _handle_parameter_specification(m, k, p):
    _norm_tol = 1e-5
    
    if m is None:
        m = np.zeros(p)
        m[0] = 1.
    else:
        m = np.asarray(m)
        try:
            assert( abs(np.linalg.norm(m) - 1.) < _norm_tol)
        except:
            raise ValueError("mean should be a unit vector")
        assert(m.size == p)

    return m, k, p
