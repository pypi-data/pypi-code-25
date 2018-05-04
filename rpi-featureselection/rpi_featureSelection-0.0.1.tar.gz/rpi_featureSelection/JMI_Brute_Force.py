from rpi_featureSelection.JointMutualInformation import JMI
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
#import random

def JMI_BF(train_data, train_label):
    
    neigh = KNeighborsClassifier(n_neighbors = 3)
    
    featureSIZE = 1;
    
    noOfFeatures = train_data.shape[1]
    noOfSamples = train_data.shape[0]
    
    test_SampleSIZE = int(np.floor(noOfSamples/3))
    #test_SampleIndex = np.zeros(shape = (test_SampleSIZE,))
    #for i in range(0, test_SampleSIZE):
    #    test_SampleIndex[i] =  random.randint(0,noOfFeatures)
    
    #test_SampleIndex = np.unique(test_SampleIndex)
    #test_SampleIndex = test_SampleIndex.astype(int)
    
    test_data = train_data[0:test_SampleSIZE, :]
    test_label = train_label[0:test_SampleSIZE]
    
    ERR_JMI = np.zeros(shape = (noOfFeatures,))
    
    features_JMI = JMI(train_data, train_label,k)
    #features_JMI = features_JMI.astype(int)
    
    feat = features_JMI[0:featureSIZE]
    neigh.fit(train_data[:, feat], train_label)

    ERR_JMI[0] = 1 - neigh.score(test_data[:,feat], test_label)
    
    MIN_ERR = ERR_JMI[0]
    MIN_SIZE = featureSIZE
    
    for featureSIZE in range(2, noOfFeatures):
        feat = features_JMI[0:featureSIZE]
        neigh.fit(train_data[:, feat], train_label)
        ERR_JMI[featureSIZE-1] = 1 - neigh.score(test_data[:, feat], test_label)
        
        if ERR_JMI[featureSIZE-1] < MIN_ERR:
            MIN_ERR = ERR_JMI[featureSIZE-1]
            MIN_SIZE = featureSIZE
            
    return features_JMI[0:MIN_SIZE]
