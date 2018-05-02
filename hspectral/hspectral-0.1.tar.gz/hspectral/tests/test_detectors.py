import sys
import numpy as np
from medpy.filter.smoothing import anisotropic_diffusion
from hspectral import generators, detectors, utils
import matplotlib.pyplot as plt
sys.path.insert(0, '../..')
from skimage.morphology import disk
from skimage.filters.rank import median
from sklearn.preprocessing import normalize

def test_RX():
    X, y = generators.generate_anomaly(random_state=2, n_anomalies = 3,
                                       a_size = 10,
                                       noise_scale = 1, shape=(100,200,50))
    sigma, inv_sigma, result = detectors.RX(X)
    detection = detectors.anisomedian_decision(result, percentile=50)

    # Plot something
    fig, ax = plt.subplots(5,1, figsize=(3,8))
    ax[0].imshow(y, cmap='gray')
    ax[0].set_title('Ground truth')

    ax[1].imshow(X[:,:,30], cmap='gray')
    ax[1].set_title('Sample band')

    ax[2].imshow(result, cmap='gray')
    ax[2].set_title('RX output')

    ax[3].imshow(detection, cmap='gray')
    ax[3].set_title("detection")

    accuracy = np.sum(detection == y) / (detection.shape[0] * detection.shape[1])

    ax[4].imshow(detection == y, cmap='gray')
    ax[4].set_title("%.3f" % accuracy)


    # remove the x and y ticks
    for a in ax:
        a.set_xticks([])
        a.set_yticks([])

    plt.savefig('bar.png')

    assert False
