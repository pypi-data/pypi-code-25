import numpy as np

def dist(a, b, ax=1):
    return np.linalg.norm(a - b, axis=ax)