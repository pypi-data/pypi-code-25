import numpy as np
import matplotlib.pyplot as plt

def generate_anomaly(shape = (100, 100, 50), n_anomalies = 2, a_size = 10,
                     random_state = None, noise_scale = .1):
    np.random.seed(random_state)

    # Assigning shape of image
    X = np.zeros(shape)
    y = np.zeros(shape[:2])

    # Establishing position of anomalies
    positions_x = np.random.random_integers(shape[0] - a_size,
                                            size = n_anomalies)
    positions_y = np.random.random_integers(shape[1] - a_size,
                                            size = n_anomalies)

    # Drawing anomalies on ground_truth
    for i in range(n_anomalies):
        y[positions_x[i]:positions_x[i]+a_size,
          positions_y[i]:positions_y[i]+a_size] = 1

    # Making class signatures
    s_attr = np.linspace(0, 2*3.1415, shape[2])

    a = .5 + np.random.random_sample()
    b = .5 + np.random.random_sample()

    anomaly_signature = (np.cos(a * s_attr) + 1)/2
    background_signature = (np.sin(b * s_attr) + 1)/2

    # Building image from Signatures
    X[y==0] = background_signature
    X[y==1] = anomaly_signature

    # Creating noise
    noise = np.abs(np.random.normal(0, noise_scale, shape))
    X += noise

    return X, y
