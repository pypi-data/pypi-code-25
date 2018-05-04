import numpy as np
from rpi_featureSelection.HillClimbing_entropy_discretization import HillClimbing_entropy_discretization
    
def  fast_feature_discretization_HC(trainD, trainL, hm_bins):
    
    samples = trainD.shape[0]
    hm_features = trainD.shape[1]

    #check the labels
    hm_unique_class = np.ceil(np.max(trainL)) - np.floor(np.min(trainL)) + 1
    edges = np.histogram(trainL, int(hm_unique_class) - 1)[1]  
    #disc_trainL = np.digitize(trainL, edges)[:,0]  #dim = (samples,)
    disc_trainL = np.digitize(trainL, edges)
    disc_trainL = np.reshape(disc_trainL, (samples,1))
    
    #Discretize the features
    disc_trainD = np.zeros([samples, hm_features])
    
    for i in range(hm_features):
        feature = trainD[:,i] #dim = (samples,)
        disc_feat,_,_ = HillClimbing_entropy_discretization(feature, disc_trainL, hm_bins, 0.01)
        
        disc_trainD[:,i] = disc_feat #dim = (samples,)
        #disc_trainD[:,i] = np.reshape(disc_feat, [samples,1])
                
    return disc_trainD, disc_trainL, hm_unique_class
