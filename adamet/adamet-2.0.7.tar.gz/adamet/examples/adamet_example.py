#!/usr/bin/env python3

"""
MODIFICATION HISTORY:
    V1.0.0: Michele Cappellari, Oxford, 25 April 2018
    V1.0.1: Adapted for consistency with changes in adamet input.
        MC, Oxford, 4 May 2018

"""

import numpy as np

from adamet.adamet import adamet   

###############################################################################

def lnprob_fun(pars, x, y, sigy):
    """
    The model is a straight line.
    This function returns the natural logarithm of

        P(model | data) ~ P(data | model) P(model)

    In this case we assume:

        1) P(model) = cost (i.e. uninformative prior)
        2) P(data | model) = likelihood for Gaussian errors

    This implies:

        P(model | data) ~ -0.5*chi^2

    """
    ymod = pars[0] + pars[1]*x
    resid = (y - ymod)/sigy
    chi2 = resid @ resid

    return -0.5*chi2   # ln(likelihood)

###############################################################################

def adamet_example():
    """
    Usage example for the adamet package.
    Fit a straight line.
    
    """
    # Generate some random (x, y) data
    prng = np.random.RandomState(123)  # Give seed for reproducible results
    ndata = 40
    a, b = 10.0, -1.0
    x = prng.uniform(0., 5., ndata)
    sigy = np.ones_like(x)  # Unit errors
    y =  prng.normal(a + b*x, sigy)

    nstep = 10000
    pars0 = np.array([a, b])   # Starting guess

    fargs = (x, y, sigy)    # Parameters to pass to the lnprob function
    sigpar = [0.5, 0.5]     # Order of magnitude of the uncertainties
    bounds = np.array([[8, -2], [12, 0]])  # [[min(a), min(b)], [max(a), max(b)]]

    # NB: For the plots to appear propely, one has to to show them in a window,
    # rather than inline, or in a notebook. When running this code from an 
    # IPhython console, one may have to type something like "%matplotlib qt5" 
    # on the console, before running the code.

    # This example matches the optimal acceptance rate of 35% in 2-dim.
    pars, like = adamet(lnprob_fun, pars0, sigpar, bounds, nstep, seed=456,
                        args=fargs, nprint=nstep/10, labels=['a', 'b'])

    bestfit = pars[np.argmax(like)]
    perc = np.percentile(pars, [15.86, 84.14], axis=0)
    sig_bestfit = np.squeeze(np.diff(perc, axis=0)/2)   # half of 68% interval
    print(f"a = {bestfit[0]:0.2f} +/- {sig_bestfit[0]:0.2f}")
    print(f"b = {bestfit[1]:0.2f} +/- {sig_bestfit[1]:0.2f}")

###############################################################################

if __name__ == '__main__':

    adamet_example()

