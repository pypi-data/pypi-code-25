# -*- coding: utf-8 -*-
"""
Created on Fri May 18 14:04:39 2018

@author: yili.peng
"""


import numpy as np
import pandas as pd

class functions:
    '''
    df: dataframe
    num: float
    both: dataframe or constant
    lg: logical df
    group: factorized dataframe
    '''
    #return df
    def choose(lg,df1,df2):
        return df1.where(cond=lg.astype(bool),other=df2)
    def absolute(df):
        return df.abs()
    def log(df):
        return np.log(df.abs()+1)
    def sign(df):
        return np.sign(df)
    def add(df,both):
        return df.add(both)
    def subtract(df,both):
        return df.subtract(both)
    def multiply(df,both):
        return df.multiply(both)
    def divide(df,both):
        if (type(both) in (float,int)) and both==0:
            return df
        elif type(both) == pd.DataFrame:
            both=both.replace(0,np.nan)
        return df.divide(both)
    def rank(df):
        return df.rank(axis=1)
    def delay(df,num):
        d=int(np.ceil(abs(num)))
        return df.shift(d)
    def correlation(df1,df2,num):
        d=int(np.ceil(abs(num)))
        r1=df1.rolling(d)
        r2=df2.rolling(d)
        return r1.corr(r2)
    def covariance(df1,df2,num):
        d=int(np.ceil(abs(num)))
        r1=df1.rolling(d)
        r2=df2.rolling(d)
        return r1.cov(r2)        
    def scale(df):
        return df.divide(df.abs().sum(axis=1),axis=0)
    def delta(df,num):
        d=int(np.ceil(abs(num)))
        return df-df.shift(d)
    def signedpower(df,num):
        if abs(num)>=3:
            num=3
        return df.pow(num)
    def linear_decay(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).apply(lambda x: np.average(x,weights=range(1,d+1)))
    def indneutralize(df,group):
        result=pd.DataFrame()
        tmp=pd.merge(left=df.stack().rename('df').reset_index(),right=group.stack().rename('group').reset_index(),\
                     on=['level_0','level_1'],how='outer').pivot(index='level_0',columns='level_1')
#        tmp=pd.concat([df.stack().rename('df'),group.stack().rename('group')],axis=1).unstack()
        for inx in tmp.index:
            df_tmp=tmp.loc[inx].unstack(level=0).infer_objects()
            df_mean=df_tmp.groupby('group').mean()
            s=df_tmp['df']-pd.Series(df_mean.reindex(df_tmp['group'])['df'].values,index=df_tmp.index)
            result=result.append(s.rename(inx))
        return result
    def ts_min(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).min()
    def ts_max(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).max()
    def ts_argmax(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).apply(np.argmax)
    def ts_argmin(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).apply(np.argmin)
    def ts_rank(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).apply(lambda x: x.argsort().argsort()[0])
    def ts_sum(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).sum()
    def ts_product(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).apply(np.product)
    def ts_std(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).std()
    #return logical lg (int 0/1)
    def le(df,both):
        return df.le(both).astype(float)
    def ge(df,both):
        return df.ge(both).astype(float)
    def or_df(lg,lg2):
        return (lg.astype(bool)|lg2.astype(bool)).astype(float)
    def eql(df,both):
        return df.eq(both).astype(float)