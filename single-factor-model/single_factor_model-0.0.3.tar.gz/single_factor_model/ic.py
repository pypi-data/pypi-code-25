# -*- coding: utf-8 -*-
"""
Created on Fri May 11 16:40:16 2018

@author: yili.peng
"""

import warnings
import numpy as np
import pandas as pd
from functools import reduce
import statsmodels.api as sm
import time as tm
from multiprocessing import Pool
from copy import deepcopy

class ic_measurement:
    def __init__(self,factor_dict={}):
        '''
        initialization
        
        factor_dict is the dictionary returned from preprocessing
        '''
        self.factor_dict=factor_dict
        warnings.simplefilter(action = "ignore", category = RuntimeWarning)  
    def __call__(self,**kwarg):
        '''
        run ic measurement
        '''        
        t0=tm.time()
        print('\n--------------------[ IC Measure Start ]--------------------')        
        self.update(**kwarg)
        M=self.ic_measure(**kwarg)
        t1=tm.time()
        print('total time: %.3f s'%(t1-t0))
        print('--------------------[ IC Measure End ]--------------------\n')
        return M
    def update(self,new_dict={},**kwarg):
        '''        
        update factor_dict      
        
        new_dict={'Factor_name1':Factor1_info,'Factor_name2':Factor2_info,...}
        Factor_info={'Return':Return_df,'Industry':Industry_df,'Factor':Factor_df,'Stock_Weight':Stock_Weight_df,'Industry_Weight':Industry_Weight_df,'Time':Time_list,'Multiple':Multiple_df}
        '''
        self.factor_dict.update(new_dict)       
    def ic_measure(self,processors=None,sub_factor=None,window=1,window_weight_decay=1,half_decay=None,**kwarg):
        '''
        regression w/ multiprocessing
        
        sub_factor: list/tuple or None(all)
        window: regression data window
        window_weight_decay: between 0 and 1 
        half_decay: (1,Inf) if half_decay is set then window_weight_decay would be ignored
        '''
        
        if sub_factor is None:
            factor_list=list(self.factor_dict.keys())
        else:
            factor_list=list(set(sub_factor) & set(self.factor_dict.keys()))
        if len(factor_list)==0:
            raise Exception('No effcient factor')
        if half_decay is not None:
            window_weight_decay=np.exp(-np.log(2)/(half_decay-1))
            
        X=[[factor,self.factor_dict[factor],window,window_weight_decay] for factor in factor_list]
        pool = Pool(processes=processors)
        multi_res=pool.map(self.ic_measure_mul, X)
        Measure={}
        for res in multi_res:
            if res[1].shape[0]>0:
                Measure[res[0]]=res[1]
        return Measure
    
    @staticmethod
    def ic_measure_mul(X):
        '''
        used in ic_measure
        '''
        factor,Dict,window,window_weight_decay=X[0],deepcopy(X[1]),X[2],X[3]
        Result=pd.DataFrame()
        for i in range(len(Dict['Time'])+1-window):               
            y_slice=Dict['Return'].iloc[i:(window+i)]
            xf_slice=Dict['Factor'].iloc[i:(window+i)]
            xi_slice=Dict['Industry'].iloc[i:(window+i)]
            xw_slice=Dict['Stock_Weight'].iloc[i:(window+i)]
            columns_intersect=list(reduce(lambda x,y: set(x)&set(y),[y_slice.columns, xf_slice.columns,xi_slice.columns,xw_slice.columns]))
         
            time_slice=Dict['Time'][i+window-1]
    
#            weight_slice=pd.DataFrame(1,index=y_slice.index,columns=columns_intersect)
#            for j in range(window):
#                weight_slice.iloc[j]*=window_weight_decay**(window-j-1)
            weight_slice=pd.DataFrame([[window_weight_decay**(window-j-1) for j in range(window)]],index=columns_intersect,columns=y_slice.index).T

            sample=pd.DataFrame({'Return':y_slice[columns_intersect].stack(dropna=False).values,factor:xf_slice[columns_intersect].stack(dropna=False).values,\
                                 'Industry':xi_slice[columns_intersect].stack(dropna=False).values,'Weight_time':weight_slice[columns_intersect].stack(dropna=False).values,\
                                'Weight_stock':xw_slice[columns_intersect].stack(dropna=False).values},index=range(np.prod(weight_slice.shape)))
            sample.dropna(axis=0,inplace=True)
            if sample.shape[0]==0:
                continue
            # regression
            y=sample['Return']
            w=sample['Weight_time']*sample['Weight_stock']
            X=sample.drop(['Return','Weight_time','Weight_stock'],axis=1)
            
            x_fac=X[factor].values
    
            med=np.median(x_fac)
            med2=np.median(np.abs(x_fac-med))
            x_fac[x_fac>(med+5*med2)]=med+5*med2
            x_fac[x_fac<(med-5*med2)]=med-5*med2
            if np.std(x_fac)==0:
                continue
            X[factor]=(x_fac-np.mean(x_fac))/np.std(x_fac)
            
            X['Industry']=X['Industry'].astype('category')
            X=pd.get_dummies(X,drop_first=True)
            X=sm.add_constant(X)
            model=sm.WLS(y,X,w)
            est=model.fit()
            t_value=est.tvalues[factor]
            coef_value=est.params[factor]                
            # ic                 
            y_ic=sample[factor]
            X_ic=sample[['Industry','Weight_stock']]
            X_ic=pd.get_dummies(X_ic,drop_first=True)
            X_ic=sm.add_constant(X_ic)
            model_ic=sm.OLS(y_ic,X_ic)
            est_ic=model_ic.fit()
            X_factor=pd.Series(est_ic.resid,index=sample.index)
            ic_value=X_factor.corr(sample['Return'],method='spearman')
            
            Result=Result.append(pd.Series([t_value,coef_value,ic_value],index=['t','coef','ic'],name=time_slice))
        return (factor,Result)