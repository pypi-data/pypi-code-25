"""
Functions for analyzing images.
"""

import matplotlib.pyplot as plt
import numpy as np


def boxcount(img, k):
    """
    Internal box counting function used by
    :func:`pyutils_sh.image.fractal_dimension`.

    From https://github.com/rougier/numpy-100 (#87)

    Parameters
    ----------
    img : ndarray
        Thresholded grayscale image for box counting.
    k : ndarray
        Array of box sizes to use.

    Returns
    -------
    count : int
        Count value.
    """

    s = np.add.reduceat(
        np.add.reduceat(img, np.arange(0, img.shape[0], k), axis=0),
        np.arange(0, img.shape[1], k), axis=1)

    # We count non-empty (0) and non-full boxes (k*k)
    return len(np.where((s > 0) & (s < k*k))[0])


def fractal_dimension(img, threshold=.5, mean_threshold=True, plot=False):
    """
    Calculate (Minkowski–Bouligand) fractal dimension.

    From https://github.com/rougier/numpy-100 (#87)

    Parameters
    ----------
    img : ndarray
        Grayscale image for box counting.
    threshold : float between [0., 1.], optional
        Value at which to binarized the image.
    mean_threshold : bool, optional
        If true, binarize image at the its mean value.
    plot : bool, optional
        Display a plot of the thresholded image.

    Returns
    -------
    fd : float
        Fractal dimension value for the image.
    """

    # Only for 2d image
    assert(len(img.shape) == 2)

    # Transform Z into a binary array
    if mean_threshold:
        threshold = np.mean(img)  # Dynamically setting threshold

    img = (img < threshold)

    if plot:
        plt.imshow(img, cmap=plt.get_cmap('gray'))
        plt.show()

    # Minimal dimension of image
    p = min(img.shape)

    # Greatest power of 2 less than or equal to p
    n = 2**np.floor(np.log(p)/np.log(2))

    # Extract the exponent
    n = int(np.log(n)/np.log(2))

    # Build successive box sizes (from 2**n down to 2**1)
    sizes = 2**np.arange(n, 1, -1)

    # Actual box counting with decreasing size
    counts = []
    for size in sizes:
        counts.append(boxcount(img, size))

    # Fit the successive log(sizes) with log (counts)
    if plot:
        plt.plot(np.log(sizes), np.log(counts))
        plt.xlabel('log(box size)')
        plt.ylabel('log(count)')
        plt.show()

    coeffs = np.polyfit(np.log(sizes), np.log(counts), 1)

    return -coeffs[0]


def rgb2gray(img):
    """
    Convert RGB image to grayscale.

    Parameters
    ----------
    img : ndarray
        Normalized (/255) image array from `scipy.misc.imread()` or
        `imageio.imread()`.

    Returns
    -------
    gray : ndarray
        Grayscale image array.
    """

    r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    gray = 299/1000 * r + 587/1000 * g + 114/1000 * b
    return gray
