from __future__ import division, print_function

import numpy as np

from .core import maximize_likelihood

class FitResult:
    '''
    Class to contain the result from the fitting routines.
    '''
    def __init__(self,p,cov,L):
        self.p = p
        self.cov = cov
        self.L = L

    def get_result(self):
        '''
        Get quickly the fitted paramters and their uncertainties (i.e. the
        square roots of the diagonal elements of the covariance matrix).
        '''
        return self.p, np.sqrt(np.diag(self.cov))

def outlier_fit(f_model,p0,x,y,sigma0,method='conservative'):
    '''
    Least squares fitting algorithm with outlier handling. Fits the given model
    f_model(x,*p) to the (x,y) data. The initial guess for the parameters p0 is
    to be given. Returns optimized p, covariance matrix cov, and the likelihood
    function L wrapped in a FitResult object.

    sigma0 has a slightly different function dependending on the used method.
    With 'conservative' sigma0 is the lower bound for the uncertainty of each
    data point upper value being unlimited. This corresponds to the prior
    sigma0/sigma^2 when sigma >= sigma0, 0 otherwise.

    With 'cauchy' the uncertainties are assumed to be of the same order as
    sigma0 but they can be either smaller or larger. The prior in this case
    is proportional to exp(-sigma0^2/sigma^2)/sigma^2.
    '''

    #define the likelihood for chi squared
    if method=='conservative':
        def L(p):
            R = (f_model(x,*p)-y)/sigma0
            return np.sum(np.log((1-np.exp(-0.5*R**2))/R**2))
    elif method=='cauchy':
        def L(p):
            R = (f_model(x,*p)-y)/sigma0
            return -np.sum(np.log(1+0.5*R**2))

    p, cov = maximize_likelihood(L,p0)
    return FitResult(p, cov, L)

def least_squares(f_model,p0,x,y,yerr=1,noise_scaling=False):
    '''
    Least squares fitting. Fits the given model f_model(x,*p) to the (x,y) data.
    The initial guess for the parameters p0 is to be given. Returns optimized p,
    covariance matrix cov, and the likelihood function L wrapped in a FitResult
    object.

    The uncertainties in y yerr can be either a float or an array.
    If error_scaling is False, then the fit is an ordinary least squares.
    If True, then yerr replaced with sigma*yerr, where sigma is treated
    as a nuisance parameter with Jeffreys' prior.
    '''

    #define the likelihood for chi squared
    if noise_scaling == False:
        def L(p):
            return -0.5*np.sum((y-f_model(x,*p))**2/yerr**2)
    else:
        def L(p):
            return -0.5*y.size*np.log(np.sum((y-f_model(x,*p))**2/yerr**2))

    p, cov = maximize_likelihood(L,p0)

    return FitResult(p, cov, L)
