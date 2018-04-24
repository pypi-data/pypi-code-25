import pandas as pd
import numpy as np
import statistics
from datetime import datetime
import math



def dataclean(data, features = []):
    ''' Takes the dataset and the feature list to run SVM on with the class-label included.
        generates a NxN numpy.ndarray depending upon the size of the dataset passed. '''
    mean = []
    SIZE = int(math.sqrt(len(data)))
    i = 0
    j = 0 
    needed = pd.DataFrame(np.vstack((data[features[0]].values, data[features[1]].values, data[features[2]].values)).T, columns=features)
    needed['tag'] = -1
    mat = np.empty((SIZE,SIZE), dtype=object)
    for x in needed.itertuples(name=None, index=False):
        mat[i][j] = np.asarray(x, dtype='float64')
        mat[i][j][3] = max(mat[i][j][1],mat[i][j][2]) + mat[i][j][0]
        mean.append(mat[i][j][3])
        j += 1
        if j == SIZE and i < SIZE:
            j=0
            i+=1
    return [mat, mean]

def organise(data, features = [], threshold='stdev'):
    ''' Spiral organiser. takes the dataset, feature list to run SVM on and the threshold value
        threshold can be any of the following:
         - mean
         - median
         - stdev (standard deviation)
        Threshold refers to the threshold value with which we swap the rows. '''
    obj = dataclean(data, features)
    mat = obj[0]
    mean = obj[1]
    if threshold=='mean':
        meanBad = statistics.mean(mean)
    elif threshold=='median':
        meanBad = statistics.median(mean)
    else:
        meanBad = statistics.stdev(mean)

    flatmat = mat.flatten()
    size_flat = len(flatmat)
    mid = (int) (size_flat/2 - 1)
    bot = size_flat - 1
    start_time = datetime.now()
    for i in range(0, mid):
        if flatmat[i][3] > meanBad and flatmat[bot][3] > meanBad:
            continue
        if flatmat[i][3] <= meanBad and flatmat[bot][3] > meanBad:
            flatmat[i], flatmat[bot] = flatmat[bot], flatmat[i]
            bot = bot -1
            continue
        if flatmat[i][3] > meanBad and flatmat[bot][3] <= meanBad:
            while flatmat[bot][3] <= meanBad:
                bot = bot-1
            continue
        if flatmat[i][3] <= meanBad and flatmat[bot][3] > meanBad:
            i = i-1
            bot = bot - 1
            if i == bot:
                break
        
    time = datetime.now() - start_time
    return [flatmat, time]

