from hspectral import utils
import numpy as np
from skimage.morphology import disk
from skimage.filters.rank import median
from sklearn.preprocessing import normalize
from medpy.filter.smoothing import anisotropic_diffusion

def RX(X):
    shape = X.shape
    M = utils.convert2d(X)
    N, p = M.shape

    # Remove the data mean
    mean_signature = np.mean(M, axis = 0)
    M -= mean_signature

    # Compute covariance matrix
    sigma = np.matrix(np.cov(M.T))
    inv_sigma = np.array(sigma.I)

    # Calculate result
    result = [
        np.abs((M[i,:][np.newaxis] @ inv_sigma @ M[i,:][np.newaxis].T)[0,0])
        for i in range(N)
    ]

    # Reshape result
    result = np.reshape(result, (shape[0], shape[1]))

    return sigma, inv_sigma, result

def anisomedian_decision(prediction_proba, niter = 5,
                         selem = disk(1), percentile = 75):
    diffusion = anisotropic_diffusion(prediction_proba,
                                      niter=niter)
    normalization = diffusion / np.linalg.norm(diffusion)
    med = median(normalization, selem)
    decision = med > np.percentile(med, 75)
    return decision
