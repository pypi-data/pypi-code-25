import sys
import matplotlib.pyplot as plt
from numpy import NaN, Inf, arange, isscalar, asarray, array

__author__ = "Eli Billauer"
__version__ = "3.4.05"
__license__ = "public domain"

def peakdet(v, delta, x = None, return_min = False, show=False):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Returns two arrays
    
    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %      
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    
    """
    
    mxposs = []
    mnposs = []
    mxs = []
    mns = []
       
    if x is None:
        x = arange(len(v))
    
    v = asarray(v)
    
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    
    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')
    
    if delta <= 0:
        sys.exit('Input argument delta must be positive')
    
    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN
    
    lookformax = True
    
    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
        
        if lookformax:
            if this < mx-delta:
                mxposs.append(mxpos)
                mxs.append(mx)
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mnposs.append(mnpos)
                mns.append(mn)
                mx = this
                mxpos = x[i]
                lookformax = True

    mxind = array(mxposs,dtype=int)
    mnind = array(mnposs,dtype=int)
    
    if show:
        plt.figure(figsize=(8, 4))
        plt.semilogy(v,'b',lw=1)
        plt.semilogy(mxind,v[mxind],'x',mec='r',mew=2, ms=8)
        plt.semilogy(mnind,v[mnind],'x',mec='g',mew=2, ms=8)
        plt.show()
    
    if return_min:
        return mxind, mnind
    else:
        return mxind
