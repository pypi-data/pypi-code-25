# -*- coding: utf-8 -*-
"""
Created on Mon May 14 15:43:05 2018

@author: yili.peng
"""
import warnings
from datetime import datetime
import pandas as pd
import numpy as np
from scipy.stats import ttest_1samp
import time as tm

def ic_measure_summary(Measure,start_time=None,end_time=None):
    '''
    Measure: result dictionary from ic_measurement
    start_time: None(all) or string/int like '20171214' 
    end_time：None(all) or string/int like '20171214'
    '''
    t0=tm.time()
    print('\r\tIC Measure Summary \t          start          ')
    warnings.simplefilter(action = "ignore", category = RuntimeWarning)  
    Result=pd.DataFrame()
    keys=list(Measure.keys())
    keys.sort()
    for factor in keys:
        stream=Measure[factor]
        if (start_time is None) and (end_time is None):
                stream_slice=stream
        elif end_time is None:
            start_time_tmp=datetime.strptime(str(start_time),'%Y%m%d')
            stream_slice=stream.loc[start_time_tmp:]
        elif start_time is None:
            end_time_tmp=datetime.strptime(str(end_time),'%Y%m%d')
            stream_slice=stream.loc[:end_time_tmp]
        else:
            start_time_tmp=datetime.strptime(str(start_time),'%Y%m%d')
            end_time_tmp=datetime.strptime(str(end_time),'%Y%m%d')
            stream_slice=stream.loc[start_time_tmp:end_time_tmp]

        t_mean=np.abs(stream_slice['t']).mean()
        t_over2=(sum(np.abs(stream_slice['t'])>2)/stream_slice.shape[0] if stream_slice.shape[0]>0 else 0)
        t_spread=t_mean/np.abs(stream_slice['t']).std()
        factor_return_mean=np.abs(stream_slice['coef']).mean()
        factor_return_t_test,_=ttest_1samp(stream_slice['coef'],0)
        ic_mean=stream_slice['ic'].mean()
        ic_std=stream_slice['ic'].std()
        ic_over0=(sum(stream_slice['ic']>0)/stream_slice.shape[0] if stream_slice.shape[0]>0 else 0)
        ir=(ic_mean/ic_std if ic_std>0 else np.nan)
        Result=Result.append(pd.Series([t_mean,t_over2,t_spread,factor_return_mean,factor_return_t_test,ic_mean,ic_std,ir,ic_over0],\
                                       index=['t_mean','t_over2','t_spread','factor_return_mean','factor_return_t_test','ic_mean','ic_std','ir','ic_over0'],name=factor))
    t1=tm.time()
    
    print('\r\tIC Measure Summary \t          finished          ')
    print('total time: %.3f s'%(t1-t0))
    return Result[['t_mean','t_over2','t_spread','factor_return_mean','factor_return_t_test','ic_mean','ic_std','ir','ic_over0']]