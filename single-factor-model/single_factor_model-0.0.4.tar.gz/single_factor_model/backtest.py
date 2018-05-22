# -*- coding: utf-8 -*-
"""
Created on Wed May  9 16:42:41 2018

@author: yili.peng
"""


import warnings
import pandas as pd
import numpy as np
import os
from datetime import datetime
from datetime import timedelta
from multiprocessing import Pool
from copy import deepcopy
import time as tm
from .global_func import seperate


class back_testing:
    def __init__(self,factor_dict={}):
        '''
        initialization
        
        factor_dict: the dictionary returned from preprocessing
        '''
        self.factor_dict=factor_dict
        warnings.simplefilter(action = "ignore", category = RuntimeWarning)
    def __call__(self,**kwarg):
        '''
        run back testing
        '''
        t0=tm.time()
        print('\n--------------------[ Back Testing Start ]--------------------')
        self.update(**kwarg)
        B=self.back_test(**kwarg)
        t1=tm.time()
        print('total time: %.3f s'%(t1-t0))
        print('--------------------[ Back Testing End ]--------------------\n')
        return B
    def update(self,new_dict={},**kwarg):
        '''    
        update factor_dict
        
        new_dict={'Factor_name1':Factor1_info,'Factor_name2':Factor2_info,...}
        Factor_info={'Return':Return_df,'Industry':Industry_df,'Factor':Factor_df,'Stock_Weight':Stock_Weight_df,'Industry_Weight':Industry_Weight_df,'Time':Time_list,'Multiple':Multiple_df}
        '''
        self.factor_dict.update(new_dict)
    
    @staticmethod
    def back_test_mul(X):
        '''
        used in back_test
        '''
        factor,Dict,n,silent,D_path,sub_industry=X[0],deepcopy(X[1]),X[2],X[3],X[4],X[5]
        df_mul=Dict['Multiple']
        df_fac=Dict['Factor']
        df_ind=(Dict['Industry'] if sub_industry is None else Dict['Industry'].loc[:,Dict['Industry'].isin(sub_industry).sum()>0])
        df_sus=Dict['Suspend']
        columns_intersect=list(set(df_mul.columns)&set(df_fac.columns)&set(df_ind.columns)&set(df_sus.columns))
        df_fac_select=df_fac[columns_intersect]
        df_ind_select=df_ind[columns_intersect]
        df_mul_select=df_mul[columns_intersect]
        df_sus_select=df_sus[columns_intersect]
        df_ind_weight_select=Dict['Industry_Weight']
        time_select=np.array(Dict['Time'])           
        Value=pd.DataFrame()       
        value_tmp=pd.Series([1000 for i in range(n)],index=['p'+str(i) for i in range(n)],name=time_select[0]-timedelta(days=1))
        Value=Value.append(value_tmp)            
        counts=0      
        all_step=df_mul_select.shape[0]
        all_suspend_flag=2 # 0 no problem; 1 traded before and all suspended; 2 never traded and all suspended; 
        for step in range(all_step):
            time=df_mul_select.index[step]
            if time<time_select[0]:
                continue
            if counts<len(time_select):
                if time>=time_select[counts]:                      
                    #change portfolio
                    sample=pd.DataFrame({'Industry':df_ind_select.iloc[counts].values,\
                                     factor:df_fac_select.iloc[counts].values,'Ticker':df_fac_select.columns,'Suspend':df_sus_select.loc[time].values})
                    sample.dropna(axis=0,inplace=True) 
                    sample1=sample.loc[sample['Suspend']==0] #check industry
                    industry_weight=df_ind_weight_select.iloc[counts][np.unique(sample1['Industry'])].fillna(0) 
                    if len(industry_weight)>0:
                        if sum(industry_weight)>0:
                            industry_weight/=sum(industry_weight)
                        else:
                            industry_weight.loc[:]=1/len(industry_weight)
                            
                        portion=pd.DataFrame()  # target weight
                        for ind in np.unique(sample1['Industry']):
                            weight_ind=industry_weight[ind]
                            ticker_ind=sample1.loc[sample1['Industry']==ind].sort_values(by=factor,ascending=False)['Ticker']
                            weight_stk=seperate(ticker_ind,n).rename(index={i:'p'+str(i) for i in range(n)})
                            weight_stk*=weight_ind
                            portion=pd.concat([portion,weight_stk],axis=1)
                        if all_suspend_flag==2:# frist time to trade
                            freeze=pd.DataFrame(index=['p'+str(i) for i in range(n)])
                            weight_time=portion # no freeze needed
                        else:
                            freeze=weight_time.loc[:,df_sus_select.loc[time]==1] # freeze weight for suspended stocks
                            weight_time=freeze.add(((1-freeze.sum(axis=1))*portion.T).T,fill_value=0)
                        all_suspend_flag=0
                        if not silent:
                            IW=pd.DataFrame([industry_weight.index,industry_weight.values],index=['Industry','industry_weight']).T
                            M=pd.concat([pd.merge(left=sample,right=IW,how='left').set_index('Ticker'),weight_time.T],\
                                             axis=1,join='outer').sort_values(by=['Industry',factor],ascending=False)
                            M.to_csv(D_path+'\\FactorDetail_'+factor+'_'+datetime.strftime(time,'%Y%m%d')+'.csv',encoding='gbk')
                        
                    else:
                        #all suspended
                        if counts==0:
                            all_suspend_flag==2 #never start to trade
                        else:
                            if all_suspend_flag==0:
                                all_suspend_flag=1
                                # same weight_time, portion, freeze 
                                M.to_csv(D_path+'\\FactorDetail_'+factor+'_'+datetime.strftime(time,'%Y%m%d')+'.csv',encoding='gbk')
                            #else all_suspend_flag==2 do nothing
                    counts+=1        

            if all_suspend_flag==2:
                value_tmp=value_tmp.rename(time)
            else:
                weight_unfreeze=freeze.loc[:,df_sus_select.loc[time]==0].sum(axis=1)                
                if weight_unfreeze.sum()>0:
                    weight_time=weight_time.subtract(freeze.loc[:,df_sus_select.loc[time]==0],fill_value=0)             
                    weight_time=weight_time.add((weight_unfreeze*portion.T).T,fill_value=0)
                    freeze.loc[:,df_sus_select.loc[time]==0]=0
                value_list=[]
                for port in Value.columns:
                    value_list.append(value_tmp.loc[port]*weight_time.loc[port].mul(df_mul_select.loc[time,weight_time.columns].fillna(1)).sum())      
                value_tmp=pd.Series(value_list,index=Value.columns,name=time)
            Value=Value.append(value_tmp)
                
        return (factor,Value)
    def back_test(self,n=5,start_time=None,end_time=None,sub_industry=None,sub_factor=None,silent=True,processors=None,D_path=None,**kwarg):
        '''
        back test w/ multiprocessing
        
        n: portfolio numbers, default=5
        start_time: None(all) or string/int like '20171214' 
        end_time：None(all) or string/int like '20171214'
        sub_factor: list/tuple or None(all)
        silent: output detail 
        D_path: detail path
        processors: number of processors
        '''
        if sub_factor is None:
            factor_list=list(self.factor_dict.keys())
        else:
            factor_list=list(set(sub_factor) & set(self.factor_dict.keys()))
        silent=(silent if D_path is not None else True)    
        if len(factor_list)==0:
            raise Exception('No effcient factor')
        if (not silent) and (not os.path.exists(D_path)):
            os.makedirs(D_path)
        X=[[factor,self.factor_dict[factor],n,silent,D_path,sub_industry] for factor in factor_list]
        pool = Pool(processes=processors)
        multi_res=pool.map(self.back_test_mul, X)  
        Backtest={res[0]:res[1] for res in multi_res}
        return Backtest