"""
#####################################################################

Copyright (C) 1999-2018, Michele Cappellari
E-mail: michele.cappellari_at_physics.ox.ac.uk

For details on the method see:
    Cappellari M., 2002, MNRAS, 333, 400
    http://adsabs.harvard.edu/abs/2002MNRAS.333..400C

Updated versions of the software are available from my web page
http://purl.org/cappellari/software

If you have found this software useful for your
research, I would appreciate an acknowledgement to use of
`the MGE fitting method and software by Cappellari (2002)'.

This software is provided as is without any warranty whatsoever.
Permission to use, for non-commercial purposes is granted.
Permission to modify for personal or internal use is granted,
provided this copyright and disclaimer are included unchanged
at the beginning of the file. All other rights are reserved.
In particular, redistribution of the code is not allowed.

#####################################################################

NAME:
    MGE_PRINT_CONTOURS

AUTHOR:
    Michele Cappellari, Astrophysics Sub-department, University of Oxford, UK

PURPOSE:
    Produces a contour plot comparing a convolved
    MGE model to the original fitted image.

CALLING SEQUENCE:
    cnt = mge_print_contours(img, ang, xc, yc, sol, binning=None, normpsf=1,
                             magrange=10, mask=None, scale=None, sigmapsf=0)

INPUTS:
    Img = array containing the image that was fitted by MGE_FIT_SECTORS
    Ang = Scalar giving the common Position Angle of the Gaussians.
        This is measured counterclockwise from the image Y axis to
        the Gaussians major axis, as measured by FIND_GALAXY.
    Xc = Scalar giving the common X coordinate in pixels of the
        center of the Gaussians.
    Yc = Scalar giving the common Y coordinate in pixels of the
        center of the Gaussians.
    SOL - Array containing a 3xNgauss array with the MGE best-fitting
        solution as produced by MGE_FIT_SECTORS:
        1) sol[0,*] = TotalCounts, of the Gaussians components.
          The relation TotalCounts = Height*(2*!PI*Sigma^2*qObs)
          can be used compute the Gaussian central surface
          brightness (Height)
        2) sol[1,*] = Sigma, is the dispersion of the best-fitting
          Gaussians in pixels.
        3) sol[2,*] = qObs, is the observed axial ratio of the
          best-fitting Gaussian components.

OPTIONAL KEYWORDS:
    BINNING - Pixels to bin together before plotting.
        Helps producing MUCH smaller PS files (default: no binning).
    NORMPSF - This is optional if only a scalar is given for SIGMAPSF,
        otherwise it must contain the normalization of each MGE component
        of the PSF, whose sigma is given by SIGMAPSF. The vector needs to
        have the same number of elements of SIGMAPSF and the condition
        TOTAL(normpsf) = 1 must be verified. In other words the MGE PSF
        needs to be normalized. (default: 1).
    MAGRANGE - Scalar giving the range in magnitudes of the equally
        spaced contours to plot, in steps of 0.5 mag/arcsec^2,
        starting from the model maximum value.
        (default: from maximum of the model to 10 magnitudes below that)
    MASK - Boolean array of size Img. False pixels indicate that they were
        not inclued in the MGE fit. They are shown in golden color.
        (Note: MASK = ~BADPIXELS)
    SCALE - The pixel scale in arcsec/pixels used for the plot axes.
        (default: 1)
    SIGMAPSF - Scalar giving the sigma of the PSF, or vector with the
        sigma of an MGE model for the circular PSF. (Default: no convolution)

EXAMPLE:
    See the file mge_fit_example.py for some usage examples.

MODIFICATION HISTORY:
    V1.0.0 First implementation, Padova, February 1999, Michele Cappellari
    V2.0.0 Major revisions, Leiden, January 2000, MC
    V2.1.0 Updated documentation, Leiden, 8 October 2001, MC
    V2.2.0 Implemented MGE PSF, Leiden, 29 October 2001, MC
    V2.3.0 Added MODEL keyword, Leiden, 30 October 2001, MC
    V2.3.1 Added compilation options, MC, Leiden 20 May 2002
    V2.3.2: Use N_ELEMENTS instead of KEYWORD_SET to test
        non-logical keywords. Leiden, 9 May 2003, MC
    V2.4.0: Convolve image with a Gaussian kernel instead of using
        the SMOOTH function before binning. Always shows contours
        in steps of 0.5 mag/arcsec^2. Replaced LOGRANGE and NLEVELS
        keywords with MAGRANGE. Leiden, 30 April 2005, MC
    V2.4.1: Added /CONVOL keyword. MC, Oxford, 23 September 2008
    V2.4.2: Use Coyote Library to select red contour levels for MGE model.
        MC, Oxford, 8 August 2011
    V3.0.0: Translated from IDL into Python.
        MC, Aspen Airport, 8 February 2014
    V3.0.1: Use input scale to label axis if given. Avoid use of log.
        Use data rather than model as reference for the contour levels.
        Allow for a scalar sigmaPSF. MC, Oxford, 18 September 2014
    V3.0.2: Fixed extent in contour plot. MC, Oxford, 18 June 2015
    V3.0.3: Fixed bug introduced by contour change in Matplotlib 1.5.
        MC, Oxford, 19 January 2016
    V3.0.4: Removed warning about non-integer indices in Numpy 1.11.
        MC, Oxford, 20 January 2017
    V3.0.5: Included `mask` keyword to identify bad pixels on the contour.
        Updated documentation. MC, Oxford, 20 March 2017
    V3.0.6: Fixed MatplotlibDeprecationWarning in Matplotlib V2.2.
        MC, Oxford. 13 April 2018

"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

#----------------------------------------------------------------------------

def _gauss2d_mge(n, xc, yc, sx, sy, pos_ang):
    """
    Returns a 2D Gaussian image with size N[0]xN[1], center (XC,YC),
    sigma (SX,SY) along the principal axes and position angle POS_ANG, measured
    from the positive Y axis to the Gaussian major axis (positive counter-clockwise).

    """
    ang = np.radians(pos_ang - 90.)
    x, y = np.ogrid[:n[0], :n[1]] - np.array([xc, yc])

    xcosang = np.cos(ang)/(np.sqrt(2.)*sx)*x
    ysinang = np.sin(ang)/(np.sqrt(2.)*sx)*y
    xsinang = np.sin(ang)/(np.sqrt(2.)*sy)*x
    ycosang = np.cos(ang)/(np.sqrt(2.)*sy)*y

    im = (xcosang + ysinang)**2 + (ycosang - xsinang)**2

    return np.exp(-im)

#----------------------------------------------------------------------------

def _multi_gauss(pars, img, sigmaPSF, normPSF, xpeak, ypeak, theta):

    lum, sigma, q = pars

    # Analytic convolution with an MGE circular Gaussian
    # Eq.(4,5) in Cappellari (2002)
    #
    u = 0.
    for lumj, sigj, qj in zip(lum, sigma, q):
        for sigP, normP in zip(sigmaPSF, normPSF):
            sx = np.sqrt(sigj**2 + sigP**2)
            sy = np.sqrt((sigj*qj)**2 + sigP**2)
            g = _gauss2d_mge(img.shape, xpeak, ypeak, sx, sy, theta)
            u += lumj*normP/(2.*np.pi*sx*sy) * g

    return u

#----------------------------------------------------------------------------

def mge_print_contours(img, ang, xc, yc, sol, binning=None, normpsf=1,
                       magrange=10, mask=None, scale=None, sigmapsf=0):

    sigmapsf = np.atleast_1d(sigmapsf)
    normpsf = np.atleast_1d(normpsf)

    assert normpsf.size == sigmapsf.size, "sigmaPSF and normPSF must have the same length"
    assert round(np.sum(normpsf)*100) == 100, "PSF not normalized"

    if mask is not None:
        assert mask.dtype == bool, "MASK must be a boolean array"
        assert mask.shape == img.shape, "MASK and IMG must have the same shape"

    model = _multi_gauss(sol, img, sigmapsf, normpsf, xc, yc, ang)
    peak = img[int(round(xc)), int(round(yc))]
    levels = peak * 10**(-0.4*np.arange(0, magrange, 0.5)[::-1]) # 0.5 mag/arcsec^2 steps

    if binning is None:
        binning = 1
    else:
        model = ndimage.filters.gaussian_filter(model, binning/2.355)
        model = ndimage.zoom(model, 1./binning, order=1)
        img = ndimage.filters.gaussian_filter(img, binning/2.355)
        img = ndimage.zoom(img, 1./binning, order=1)

    ax = plt.gca()
    ax.axis('equal')
    ax.set_adjustable('box')
    s = img.shape

    if scale is None:
        extent = [0, s[1], 0, s[0]]
        plt.xlabel("pixels")
        plt.ylabel("pixels")
    else:
        extent = np.array([0, s[1], 0, s[0]])*scale*binning
        plt.xlabel("arcsec")
        plt.ylabel("arcsec")

    cnt = ax.contour(img, levels, colors = 'k', linestyles='solid', extent=extent)
    ax.contour(model, levels, colors='r', linestyles='solid', extent=extent)
    if mask is not None:
        a = np.ma.masked_array(mask, mask)
        ax.imshow(a, cmap='autumn_r', interpolation='nearest', origin='lower',
                  extent=extent, zorder=3, alpha=0.7)

    return cnt

#----------------------------------------------------------------------------
