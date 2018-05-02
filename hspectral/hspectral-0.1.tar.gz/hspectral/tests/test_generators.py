import sys
from hspectral import generators
import matplotlib.pyplot as plt
sys.path.insert(0, '../..')


def test_anomaly_generator():
    X, y = generators.generate_anomaly(random_state=1, n_anomalies = 4,
                                       noise_scale = .3)
    """
    fig, ax = plt.subplots(4,1, figsize=(2,8))
    ax[0].imshow(y, cmap='gray')
    ax[0].set_title('Ground truth')
    ax[1].imshow(X[:,10,:], cmap='gray')
    ax[1].set_title('Przekrój po pasmach')
    ax[2].imshow(X[:,:,20], cmap='gray')
    ax[2].set_title('Przekroje po warstwach')
    ax[3].imshow(X[:,:,40], cmap='gray')

    for a in ax:
        a.set_xticks([])
        a.set_yticks([])

    plt.savefig('foo.png')
    """
