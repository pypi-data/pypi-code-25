""""""
import os
import gzip
import numpy as np

SRC_PATH = r"D:\OneDrive\workspace\data\image\mnist-fashion"
NPZ_PATH = r"D:\OneDrive\workspace\data\image\mnist-fashion\mnist-fashion.npz"


def load_data(dir_path=SRC_PATH):
    """
    从源文件加载数据

    下载地址：http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/

    Args:
        dir_path(str):  文件所在文件夹，包括 4 个文件：
            ['train-images-idx3-ubyte.gz',
             'train-labels-idx1-ubyte.gz',
             't10k-images-idx3-ubyte.gz',
             't10k-labels-idx1-ubyte.gz']

    Returns:

    """

    files = ['train-labels-idx1-ubyte.gz', 'train-images-idx3-ubyte.gz',
             't10k-labels-idx1-ubyte.gz', 't10k-images-idx3-ubyte.gz']
    paths = [os.path.join(dir_path, fname) for fname in files]

    with gzip.open(paths[0], 'rb') as lbpath:
        y_train = np.frombuffer(lbpath.read(), np.uint8, offset=8)

    with gzip.open(paths[1], 'rb') as imgpath:
        x_train = np.frombuffer(imgpath.read(), np.uint8,
                                offset=16).reshape(len(y_train), 28, 28)

    with gzip.open(paths[2], 'rb') as lbpath:
        y_test = np.frombuffer(lbpath.read(), np.uint8, offset=8)

    with gzip.open(paths[3], 'rb') as imgpath:
        x_test = np.frombuffer(imgpath.read(), np.uint8,
                               offset=16).reshape(len(y_test), 28, 28)

    return (x_train, y_train), (x_test, y_test)


def load_data_npz(file_path=NPZ_PATH):
    """
    从 .npz 文件加载数据

    Args:
        file_path(str):

    Returns:

    """
    with np.load(file_path) as f:
        x_train, y_train = f['x_train'], f['y_train']
        x_test, y_test = f['x_test'], f['y_test']
    return (x_train, y_train), (x_test, y_test)
