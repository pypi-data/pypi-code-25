""""""
from .mnist import load_data as load_mnist
from .mnist_fashion import load_data as load_mnist_fashion
from .imdb import load_data as load_imdb

import numpy as np


def save_to_npz(file: str, compressed=True, *args, **kwargs):
    """
    保存到 .npz 文件

    Examples:
        save_to_npz("weight.npz", x_train=x_train, x_test=x_test, y_train=y_train, y_test=y_test)
    """
    if compressed:
        np.savez_compressed(file, *args, **kwargs)
    else:
        np.savez(file, *args, **kwargs)


