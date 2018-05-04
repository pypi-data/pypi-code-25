import numpy as np

def findOptimalSplitPoint(min_val, max_val, ori_feat, label, incre_rate = 0.1):
    
    hm_bins = round(1/incre_rate)
    splits = np.linspace(min_val, max_val, hm_bins+1)
    hm_class = len(np.unique(label))
    
    if hm_class <= 1:
        min_entropy = 0
        optimal_split = max_val
                
        return optimal_split, min_entropy
    
    
    #edges = np.histogram(label, hm_class-1)[1]
    #label = np.digitize(label, edges)
    
    hm_sample = len(label)
    
    entropies = np.zeros(hm_bins,)
    
    for i in range(1, hm_bins+1):
        split = splits[i]
        count_inbin = np.histogram(ori_feat, [min_val, split, max_val])[0]
        Bin = np.digitize(ori_feat, [min_val, split, max_val])
        
        #the first bin
        num_data = np.zeros(hm_class,)
        entr_left = 0
        for c in range(hm_class):
            prob = num_data[c]/(count_inbin[0] + 1e-5)
            if prob != 0 and ~np.isnan(prob):
                entr_left = entr_left - prob*np.log2(prob)
        
        #the second bin
        num_data = np.zeros(hm_class,)
        entr_right = 0
        for c in range(hm_class):
            get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]
            index = get_indexes(2, Bin)
            if index: #check if list is empty
                temp_label = label[np.array(index)]
                index = get_indexes(c+1, temp_label) #label is starting from one
                num_data[c] = len(index)
            else:
                num_data[c] = 0
            prob = num_data[c]/(count_inbin[1] + 1e-5)
            if prob != 0 and ~np.isnan(prob):
                entr_right = entr_right - prob*np.log2(prob)
        entropies[i-1] = count_inbin[0]/hm_sample * entr_left + count_inbin[1] / hm_sample * entr_right
        
    min_entropy = np.amin(entropies)
    idx = np.where(entropies == min_entropy)
    if len(idx[0]) != 1:
        idx = idx[0][0]
    else:
        idx = idx[0]          #only return idx for the first minimul element
    optimal_split = splits[idx+1]
        
    
    return optimal_split, min_entropy