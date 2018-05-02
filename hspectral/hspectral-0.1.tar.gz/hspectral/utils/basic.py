import numpy as np

def convert2d(X, y = None):
    bands = X.shape[2]
    points = X.shape[0] * X.shape[1]
    X_2d = np.reshape(X, (points, bands))
    if y is None:
        return X_2d
    else:
        y_2d = np.reshape(y, (points))
        return X_2d, y_2d

def convert3d(X, shape, y=None):
    h, w, bands = shape
    X_3d = np.reshape(X, (h, w, bands))
    y_3d = np.reshape(y, (h, w))
    return X_3d, y_3d
