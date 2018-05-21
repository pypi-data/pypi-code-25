"""
################################################################################

    Copyright (C) 2012-2018, Michele Cappellari
    E-mail: michele.cappellari_at_physics.ox.ac.uk

    Updated versions of the software are available from my web page
    http://purl.org/cappellari/software

    If you have found this software useful for your research,
    I would appreciate an acknowledgement to the use of the
    "adamet Python package of Cappellari et al. (2013a), which implements
     the Adaptive Metropolis algorithm of Haario et al. (2001)".

    This software is provided as is without any warranty whatsoever.
    Permission to use, for non-commercial purposes is granted.
    Permission to modify for personal or internal use is granted,
    provided this copyright and disclaimer are included unchanged
    at the beginning of the file. All other rights are reserved.
    In particular, redistribution of the code is not allowed.

################################################################################

NAME:
    adamet()

PURPOSE:
    This is the implementation of

    Cappellari et al. 2013a, MNRAS, 432, 1709
        http://adsabs.harvard.edu/abs/2013MNRAS.432.1709C

    of the Adaptive Metropolis algorithm by
    
    Haario H., Saksman E., Tamminen J., 2001, Bernoulli, 7, 223
        https://projecteuclid.org/euclid.bj/1080222083

USAGE EXAMPLES:
    See the adamet_example.py
    For dimensions = 1 to 6, the optimal acceptance rates are
    rate = [0.441, 0.352, 0.316, 0.279, 0.275, 0.266]
    and the asymptotic value for many parameters is 23%
    
REQUIRED ROUTINES:
    The plotbin package is required for plotting in corner_plot
        http://purl.org/cappellari/software

MODIFICATION HISTORY:
    V1.0.0: Michele Cappellari, Oxford, 27 January 2012
    V1.1.0: Implemented Adaptive Metropolis Algorithm. MC, Oxford, 10 February 2012
    V1.2.0: Add diagonal matrix to prevent possibly degenerate covariance matrix.
        MC, Oxford, 10 August 2012
    V1.2.1: Do not sort likelihood in output. MC, Oxford, 25 October 2012
    V2.0.0: Translated from IDL into Python . MC, Atlantic Ocean, 9 February 2014
    V2.0.1: Clip input parameters to bounds. MC, Oxford, 18 February 2015
    V2.0.2: Allow for both args and kwargs parameter to the user function.
        Dropped Python 2.7 support. Minor code refactoring.
        MC, Oxford, 13 October 2017
    V2.0.3: First released version. Organized into a package.
        MC, Oxford, 25 April 2018
    V2.0.4: Ensures the user function cannot affect the random chain.
        MC, Oxford, 27 April 2018
    V2.0.5: Some changes to the input format. MC, Oxford, 4 May 2018

"""

import numpy as np
import matplotlib.pyplot as plt
from time import clock

from adamet.corner_plot import corner_plot

###############################################################################

def _move(pars, sigpars, all_pars, prng):
    """
    Adaptive move

    """
    nu = np.unique(all_pars[:, 0]).size
    npars = pars.size

    # Accumulate at least as many *accepted* moves as the
    # elements of the covariance matrix before computing it.
    if nu > npars*(npars + 1.)/2.:

        eps = 0.01
        diag = np.diag((sigpars*eps)**2)
        cov = 2.38**2/npars*(np.cov(all_pars.T) + diag)
        pars = prng.multivariate_normal(pars, cov)

    else:

        pars = prng.normal(pars, sigpars)

    return pars

###############################################################################

def _metro(lnprob_fun, pars, bounds, lnprob, try_pars, prng, args, kwargs):
    """
    Metropolis step

    """
    # Moves out of bounds are rejected without function evaluation
    if np.all((try_pars >= bounds[0]) & (try_pars <= bounds[1])):

        try_lnprob = lnprob_fun(try_pars, *args, **kwargs)
        lnran = np.log(prng.uniform())
        lnratio = try_lnprob - lnprob

        if (try_lnprob > lnprob) or (lnran < lnratio):

            pars = try_pars   # Candidate point is accepted
            lnprob = try_lnprob

    return pars, lnprob

###############################################################################

def adamet(lnprob_fun, pars, sigpars, bounds, nstep,
           labels=None, nprint=100, quiet=False, fignum=None, plot=True,
           labels_scaling=1, seed=None, args=(), kwargs={}):

    pars = np.array(pars)  # Make copy to leave input unchanged
    sigpars = np.array(sigpars)
    bounds = np.array(bounds)

    assert pars.size == sigpars.size == bounds.shape[1], \
        "pars, sigpars, and bounds must have the same size"

    if labels is not None:
        assert len(labels) == pars.size, "There must be one label per parameter"

    prng = np.random.RandomState(seed)  # Random stream independent of global one

    t = clock()

    pars = pars.clip(*bounds)  # clip parameters within bounds
    lnprob = lnprob_fun(pars, *args, **kwargs)
    all_pars = np.zeros((nstep, pars.size))
    all_lnprob = np.zeros(nstep)
    all_try_pars = np.zeros_like(all_pars)

    if plot:
        fig = corner_plot(all_pars, init=True, fignum=fignum)
        plt.pause(0.01)

    for j in range(nstep):

        try_pars = _move(pars, sigpars, all_pars[:j], prng)
        pars, lnprob = _metro(lnprob_fun, pars, bounds, lnprob, try_pars, prng, args, kwargs)

        all_pars[j] = pars  # Store only accepted moves or duplicates (when move is rejected)
        all_lnprob[j] = lnprob
        all_try_pars[j] = try_pars  # Store all attempted moves for plotting parameters coverage

        if ((j + 1) % nprint) == 0: # Just plotting/printing inside this block

            nu = np.unique(all_pars[:j, 0]).size
            if quiet is False:
                print('adamet: %0.1f %% done; %0.1f %% accepted' % 
                        (100.*(j + 1)/nstep, 100.*nu/(j + 1)))

            if plot and j > 1:
                corner_plot(all_pars[:j], all_lnprob[:j], xstry=all_try_pars[:j],
                            labels=labels, extents=bounds, fig=fig,
                            labels_scaling=labels_scaling)
                plt.pause(0.01)

    if quiet is False:
        print('adamet: done. Total time %0.2f seconds' % (clock() - t))

    return all_pars, all_lnprob

###############################################################################
