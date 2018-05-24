import os
import shutil
import numpy as np


def save_parameters(param):
    # save parameters to .npy
    # delete the 'params' folder if it exists
    if os.path.exists('params'):
        raise Exception("You must have a empty folder named 'params' in current folder")
        # shutil.rmtree('params')

    # create folders for storing parameters
    os.mkdir('params')
    os.mkdir('params/w')
    os.mkdir('params/b')
    n_task = len(param)
    num_w = len(param[0].w)
    num_b = len(param[0].b)
    for idx in range(n_task):
        for wi in range(num_w):
            np.save('params/w/w' + str(idx) + str(wi) + '.npy', param[idx].w[wi])
        for bi in range(num_b):
            np.save('params/b/b' + str(idx) + str(bi) + '.npy', param[idx].b[bi])
