# -*- coding: utf-8 -*-
"""
Created on Tue May  8 13:30:40 2018

@author: yili.peng
"""

import pandas as pd
from copy import deepcopy
import numpy as np

def split_time(s):
    '''
    get date time from file names
    '''
    return list(filter(None,list(filter(None,s.split('.')))[0].split('_')))[-1]
def read_file(file,**kwag):
    '''
    read csv files with different encodings
    '''
    try:
        df=pd.read_csv(filepath_or_buffer=file,encoding='utf-8',**kwag)
    except UnicodeDecodeError:
        df=pd.read_csv(filepath_or_buffer=file,encoding='gbk',**kwag)
    return df
def read_file_wrap(time_span,time_oneday,file_name,**kwag):
    '''
    read csv files within a time span
    '''
    if (time_span[0] is None) and (time_span[1] is None):
           return read_file(file_name,**kwag)
    elif (time_span[0] is None):
        if (time_oneday<=time_span[1]):
            return read_file(file_name,**kwag)
    elif (time_span[1] is None):
        if (time_span[0]<=time_oneday):
            return read_file(file_name,**kwag)
    else:
        if (time_oneday<=time_span[1]) and (time_span[0]<=time_oneday):
            return read_file(file_name,**kwag)
    return None
def seperate(l,n):
    '''
    calculate the weight of each element from l in n portfolios
    used in  back_test
    '''
    k=len(l)
    if k==1:
        return pd.DataFrame([1.0]*n,columns=l,index=range(n))
    shares=[1]*k
    weights=pd.DataFrame(0,columns=l,index=range(n))
    col=0
    row=0
    a=k/float(n)
    while row<n:
        a-=shares[col]
        if a>1e-5:
            weights.iloc[row,col]=shares[col]
            shares[col]=0
            col+=1
        else:
            weights.iloc[row,col]=shares[col]+a
            shares[col]=-a
            row+=1
            a=k/float(n)
    weights_st=weights/a
    return weights_st
def pre_sus(x):
    '''
    for new stocks detection and recording
    '''
    y=deepcopy(x)
    if x.isnull().any():
        i=np.where(x.isnull())[0][-1]  
        if i==0:
            y.iloc[i:(i+20)]=1
        y.fillna(1,inplace=True) 
    return y