import numpy as np
from rpi_featureSelection.findOptimalSplitPoint import findOptimalSplitPoint

def HillClimbing_entropy_discretization(feature, label, num_bins, relative_entropy_reduce_rate = 0.01):
    
    hm_class = len(np.unique(label))
    
    #edges = np.histogram(label, hm_class-1)[1]
    #label = np.digitize(label, edges)
    
    min_val = min(feature)
    max_val = max(feature)
    curr_entropy = 0
    
    pre_entropy= 0
    for i in range(hm_class):
        
        get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]
        index = get_indexes(i+1, label)  #label starts from 1
        prob = len(index)/feature.shape[0]
        if prob != 0:
            pre_entropy = pre_entropy - prob * np.log2(prob)
    
    
    if len(np.unique(feature)) > 15:
        init_splitset = np.linspace(min_val, max_val, num_bins+1)
        
        stop_flag = 0
        while stop_flag == 0:
            minentropy_inbin = np.zeros(num_bins,) #dim = (10,)
            curr_entropy = 0
            for s in range(1, num_bins):
                sub_min = init_splitset[s-1]
                sub_max = init_splitset[s+1]
                get_indexes = lambda x1,x2,xs: [i for (y, i) in zip(xs, range(len(xs))) if  y >= x1 and y < x2]
                index = get_indexes(sub_min, sub_max, feature)
                if index:
                    index = np.array(index)
                    feat = feature[index]
                    lab = label[index]
                else:
                    feat = []
                    lab = []
                init_splitset[s], minentropy_inbin[s-1] = findOptimalSplitPoint(sub_min, sub_max, feat, lab, 0.1)
                
            count_inbin = np.histogram(feature, init_splitset)[0]
            bins = np.digitize(feature, init_splitset)
            
            num_data = np.zeros(hm_class,)
            
            for n in range(num_bins):
                en = 0
                for c in range(hm_class):
                     get_indexes = lambda x1,x2,xs: [i for (y, i) in zip(xs, range(len(xs))) if  y >= x1 and y < x2]
                     index = get_indexes(init_splitset[n], init_splitset[n+1], feature)
                     if index:
                         index = np.array(index)
                         sub_lab = label[index]
                         get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]
                         index = get_indexes(c+1, sub_lab) #label is starting from 1
                         num_data[c] =  len(index)
                     else:
                        num_data[c] = 0                       
                     if num_data[c] != 0:
                         en = en - num_data[c] / count_inbin[n] * np.log2(num_data[c]/count_inbin[n])
                    
                curr_entropy = curr_entropy + en*count_inbin[n]/feature.shape[0]
                
            if curr_entropy < 0.0000001:
                stop_flag = 1
                continue
            
            relative_reduction = (pre_entropy - curr_entropy) /pre_entropy
            if relative_reduction < relative_entropy_reduce_rate:
                stop_flag = 1
                
            pre_entropy = curr_entropy
            
        discretized_feature = bins
         
    else:
        hm_unique_state = len(np.unique(feature))
        init_splitset = hm_unique_state
        if hm_unique_state != 1:
            edges = np.histogram(feature, hm_unique_state-1)[1]
            discretized_feature = np.digitize(feature, edges)
        else:
            discretized_feature = feature
            
        curr_entropy = pre_entropy
        
    
    optimal_split_pointset = init_splitset
    final_entropy = curr_entropy
    
    
    return discretized_feature, optimal_split_pointset, final_entropy       
                     
                     
    
    
