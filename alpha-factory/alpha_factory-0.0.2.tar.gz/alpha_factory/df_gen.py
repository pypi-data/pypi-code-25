# -*- coding: utf-8 -*-
"""
Created on Fri May 18 14:12:43 2018

@author: yili.peng
"""

import pandas as pd
import numpy as np
import pkg_resources

def random_number_generator():
    return np.random.randn()*10

def df_gen(func_df,frame_df,out_name):
    notfound=True
    while notfound:
        inx=np.random.choice(func_df.index)
        notfound=False
        func_name='functions.'+func_df.loc[inx,'function_name']
        func_parm=func_df.loc[inx,'parameters']
        func_oput=func_df.loc[inx,'output']
        out_parms=[]
        out_dependency=[]
        for p in func_parm.split(','):
            if p[:2] == 'df':
                flag=(frame_df['type']=='df')
                if flag.sum()==0:
                    notfound=True
                else:
                    in_df=np.random.choice(frame_df.loc[flag,'df_name'])
                    out_parms.append(in_df)
                    out_dependency.append(in_df)
            elif p[:2] == 'nu':
                out_parms.append(str(random_number_generator()))
            elif p[:2] == 'bo':
                if np.random.choice([True,False]):
                    out_parms.append(str(random_number_generator()))
                else:
                    flag=(frame_df['type']=='df')
                    if flag.sum()==0:
                        out_parms.append(str(random_number_generator()))
                    else:
                        in_df=np.random.choice(frame_df.loc[flag,'df_name'])
                        out_parms.append(in_df)
                        out_dependency.append(in_df)
            elif p[:2] == 'gr':
                flag=(frame_df['type']=='group')
                if flag.sum()==0:
                    notfound=True
                else:
                    in_df=np.random.choice(frame_df.loc[flag,'df_name'])
                    out_parms.append(in_df)
                    out_dependency.append(in_df)
            elif p[:2]== 'lg':
                flag=(frame_df['type']=='lg')
                if flag.sum()==0:
                    notfound=True
                else:
                    in_df=np.random.choice(frame_df.loc[flag,'df_name'])
                    out_parms.append(in_df)
                    out_dependency.append(in_df)
    return pd.Series([out_name,func_name+'('+','.join(out_parms)+')',','.join(out_dependency),func_oput],index=['df_name','equation','dependency','type'])

def generator(num,origin_frames_path,frame_out_path,start_name='a'):
    frame_df=pd.read_csv(origin_frames_path)
    trading_dt_path = pkg_resources.resource_filename('alpha_factory', 'data/functions.csv')
    func_df=pd.read_csv(trading_dt_path)
    for i in range(num):
        s=df_gen(func_df=func_df,frame_df=frame_df,out_name=start_name+str(i))
        frame_df=frame_df.append(s,ignore_index=True)
    frame_df.to_csv(frame_out_path,index=False)
