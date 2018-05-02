
import morphsnakes

import numpy as np
from scipy.misc import imread
from matplotlib import pyplot as ppl

def rgb2gray(img):
    """Convert a RGB image to gray scale."""
    return 0.2989*img[:,:,0] + 0.587*img[:,:,1] + 0.114*img[:,:,2]

def circle_levelset(shape, center, sqradius, scalerow=1.0):
    """Build a binary function with a circle as the 0.5-levelset."""
    grid = np.mgrid[map(slice, shape)].T - center
    phi = sqradius - np.sqrt(np.sum((grid.T)**2, 0))
    u = np.float_(phi > 0)
    return u

def test_nodule():
    # Load the image.
    img = imread("testimages/mama07ORI.bmp")[...,0]/255.0

    # g(I)
    gI = morphsnakes.gborders(img, alpha=1000, sigma=5.48)

    # Morphological GAC. Initialization of the level-set.
    mgac = morphsnakes.MorphGAC(gI, smoothing=1, threshold=0.31, balloon=1)
    mgac.levelset = circle_levelset(img.shape, (100, 126), 20)

    # Visual evolution.
    ppl.figure()
    morphsnakes.evolve_visual(mgac, num_iters=45, background=img)

def test_starfish():
    # Load the image.
    imgcolor = imread("testimages/seastar2.png")/255.0
    img = rgb2gray(imgcolor)

    # g(I)
    gI = morphsnakes.gborders(img, alpha=1000, sigma=2)

    # Morphological GAC. Initialization of the level-set.
    mgac = morphsnakes.MorphGAC(gI, smoothing=2, threshold=0.3, balloon=-1)
    mgac.levelset = circle_levelset(img.shape, (163, 137), 135, scalerow=0.75)

    # Visual evolution.
    ppl.figure()
    morphsnakes.evolve_visual(mgac, num_iters=110, background=imgcolor)

def test_lakes():
    # Load the image.
    imgcolor = imread("testimages/lakes3.jpg")/255.0
    img = rgb2gray(imgcolor)

    # MorphACWE does not need g(I)

    # Morphological ACWE. Initialization of the level-set.
    macwe = morphsnakes.MorphACWE(img, smoothing=3, lambda1=1, lambda2=1)
    macwe.levelset = circle_levelset(img.shape, (80, 170), 25)

    # Visual evolution.
    ppl.figure()
    morphsnakes.evolve_visual(macwe, num_iters=190, background=imgcolor)


def test_local_smoothing():
    import matplotlib.pyplot as plt
    # Prepare data
    sh = [40, 40]
    sh2 = sh[0]/2

    data_noise = (np.random.random(sh) * 5).astype(np.int8)
    data_noise[10:-10, 10:-10] += 10

    init_levelset = np.zeros(sh, dtype=np.int8)
    init_levelset[sh2-5:sh2+5, sh2-5:sh2+5] = 1

    mask = np.zeros(sh)
    mask[:sh2, sh2:] = 0
    mask[sh2:, sh2:] = 1
    mask[sh2:, :sh2] = 2
    mask[:sh2, :sh2] = 8

    # Run snakes
    macwe = morphsnakes.MorphACWE(data_noise, smoothing=1, smooth_map=mask)
    macwe.set_levelset(init_levelset)
    macwe.run(20)

    # Show outputs
    ax = plt.subplot(131)
    plt.imshow(data_noise, cmap='gray', interpolation='nearest')
    ax.set_title('Input data')
    ax = plt.subplot(132)
    plt.imshow(mask, cmap='gray', interpolation='nearest')
    ax.set_title('Smooth Map')
    ax = plt.subplot(133)
    plt.imshow(macwe.levelset > 0, cmap='gray', interpolation='nearest')
    ax.set_title('Output Levelset')


def test_confocal3d():

    # Load the image.
    img = np.load("testimages/confocal.npy")

    # Morphological ACWE. Initialization of the level-set.
    macwe = morphsnakes.MorphACWE(img, smoothing=1, lambda1=1, lambda2=2)
    macwe.levelset = circle_levelset(img.shape, (30, 50, 80), 25)

    # Visual evolution.
    morphsnakes.evolve_visual3d(macwe, num_iters=200)

if __name__ == '__main__':
    print("""""")
    test_nodule()
    test_starfish()
    # test_local_smoothing()
    test_lakes()
    test_confocal3d()
    ppl.show()
