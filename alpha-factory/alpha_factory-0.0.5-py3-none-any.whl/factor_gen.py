# -*- coding: utf-8 -*-
"""
Created on Fri May 18 14:31:07 2018

@author: yili.peng
"""

from .basic_functions import functions
from RNWS import write,read
from glob import glob

def find_dependency(df):
    return tuple(df.index[df['dependency'].isnull()])

def generator_batch(df,batch_size,out_file_path,**parms):
    df_tmp=df.loc[df['exists']==0].iloc[:batch_size]
    for key,df in parms.items():
        exec(key+'=parms[\''+key+'\']')
    d={}
    all_step=df_tmp.shape[0]
    step=0
    print('generating start')
    for inx in df_tmp.index:
        step+=1
        print('\rgenerating  ['+'>'*((step*30)//all_step)+' '*(30-(step*30)//all_step)+']',end='\r')
        exec(inx+'='+df_tmp.loc[inx,'equation'] )
        d.update({inx:eval(inx)})
    print('\ngenerating finished')
    parms.update(d)
    write.write_factors(path=out_file_path,file_pattern='factor',**d)
    return parms
    
def find_all_factors(path):
    pathlist=[[i,glob(i+'/factor_[0-9]*.csv')[1]] for i in glob(path+'/factor_part[0-9]*')]
    factor_list=[]
    for p in pathlist:
        line=open(p[1],'r').readline()
        factor_list.append([p[0],line.strip('\n').split(',')[1:]])
    return factor_list

def find_part(path):
    try:
        a=max([int(i[-3:]) for i in glob(path+'/*')])+1
    except:
        a=0
    return a

class generator_class:
    def __init__(self,df,factor_path,**parms):
        '''
        df: factor dataframe
        factor_path: root path to store factors
        **parms: all dependency dataframes
        '''
        flag=[i in parms.keys() for i in df.index[df['dependency'].isnull()]]
        if not all(flag):
            print('dependency:',find_dependency(df))
            raise Exception('need all dependencies')
        self.parms=parms
        self.df=df
        self.df['exists']=0
        self.df.loc[self.parms.keys(),'exists']=1
        self.batch_num=find_part(factor_path)
        self.factor_path=factor_path
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    def reload_factors(self,**kwargs):
        factor_list=find_all_factors(self.factor_path)
        if len(factor_list)==0:
            pass
        else:
            for l in find_all_factors(self.factor_path):
                path=l[0]
                factors=l[1]
                print('reload: ',path)
                factor_exposures=read.read_df(path=path,file_pattern='factor',header=0,dat_col=factors,**kwargs)
                self.parms.update({factors[i]:factor_exposures[i] for i in range(len(factors))})
            self.df.loc[self.parms.keys(),'exists']=1
    def generator(self,batch_size=50):
        new_parms=generator_batch(self.df,batch_size=batch_size,out_file_path=self.factor_path+'/factor_part'+str(self.batch_num).zfill(3),**self.parms)
        self.parms.update(new_parms)
        self.batch_num+=1
        self.df.loc[self.parms.keys(),'exists']=1