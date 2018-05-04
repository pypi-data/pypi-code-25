from rpi_featureSelection.tian_IPCMB import IPCMB
from rpi_featureSelection.joint import joint
import numpy as np
from rpi_featureSelection.ConditionalMutualInformation import cmi


def Large_Scale_IPCMB(data, targets, threshold):
    #data is training data without label column
    numfeat = data.shape[1]
    subsize = 100
    count = 0
    Feat = []
    while count*subsize <= numfeat:
        if (count + 1)*subsize <= numfeat:
            sub_D = data[:, count*subsize : subsize+count*subsize]
            results = IPCMB(sub_D, targets, threshold)
            index = results[0] + count*subsize
            Feat = set(Feat).union(set(index))
        else:
            sub_D = data[:, count*subsize :]
            results = IPCMB(sub_D, targets, threshold)
            index = results[0] + count*subsize
            Feat = set(Feat).union(set(index))
        count = count + 1
    
    Feat = list(Feat) #convert set object to list
    cmbVector = joint(data[:, Feat])
    for i in np.setdiff1d(np.arange(numfeat), Feat):
        temp = cmi(data[:,i], targets, cmbVector)
        if temp > threshold:
            Feat.append(i)
    
    MB = Feat
    return MB
