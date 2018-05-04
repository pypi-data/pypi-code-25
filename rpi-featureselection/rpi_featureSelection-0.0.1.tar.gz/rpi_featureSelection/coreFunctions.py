from rpi_featureSelection.tian_STMB_new import tian_STMB_new
from rpi_featureSelection.Large_Scale_STMB import Large_Scale_STMB
from rpi_featureSelection.fast_feature_discretization_HC import fast_feature_discretization_HC
from rpi_featureSelection.tian_IPCMB import IPCMB
from rpi_featureSelection.Large_Scale_IPCMB import Large_Scale_IPCMB
from rpi_featureSelection.JointMutualInformation import JMI

def STMBplus(trainD, trainL, thres):
    # discretize 
    hm_states = 10
    disc_trainD, disc_trainL,_ = fast_feature_discretization_HC(trainD, trainL, hm_states) #disc_trainL: (samples,1); disc_trainD: (samples, feat_num)
    
    
    feat_num = trainD.shape[1]
    if feat_num > 150:
        select_feat = Large_Scale_STMB(disc_trainD, disc_trainL, thres) #trainD is not including label column
    else:
        select_feat = tian_STMB_new(disc_trainD, disc_trainL, thres)[0]
    
    return select_feat
    
    
def IPCMBplus(trainD, trainL, thres):
    #discretize
    hm_states = 10
    disc_trainD, disc_trainL,_ = fast_feature_discretization_HC(trainD, trainL, hm_states) #disc_trainL: (samples,1); disc_trainD: (samples, feat_num)
    
    feat_num = trainD.shape[1]
    if feat_num > 150:
        select_feat = Large_Scale_IPCMB(disc_trainD, disc_trainL, thres)
    else:
        select_feat = IPCMB(disc_trainD, disc_trainL, thres)[0]
    
    return select_feat

def JMI_function(trainD, trainL, k):
    hm_states = 10
    disc_trainD, disc_trainL, _ = fast_feature_discretization_HC(trainD, trainL, hm_states) # disc_trainL:(samples,1); disc_trainD: (samples, feat_num)
    
    select_feat = JMI(disc_trainD, disc_trainL, k)
    
    return select_feat
