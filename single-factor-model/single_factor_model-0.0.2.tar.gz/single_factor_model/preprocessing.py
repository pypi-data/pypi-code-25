# -*- coding: utf-8 -*-
from . import global_func
import pandas as pd
import numpy as np
import warnings
from datetime import datetime
from datetime import timedelta
from glob import glob
from copy import deepcopy
from multiprocessing import Pool
import time as tm

class preprocessing:
    '''
    preprocessing
   
    read in tables and align date time w/ all tables
    return a dictionary with keys as factor names and values as factor dataframes.
    '''
    def __init__(self,renewal_flag='monthly',renewal_date=None,day_lag=1):
        '''
        initialization
            
        renewal_flag: renewal period, can be 'monthly' or 'daily'.
        renewal_date: the date to renewal factors. For monthly update only.
        day_lag: the lag of days to obtain factors. default day_lag. If renewal_date is not None, renewal_date is used
        '''
        if renewal_flag not in ('monthly','daily'):
            raise Exception('flag must be "monthly" or "daily"')
        self.dict={}
        self.Industry=pd.DataFrame()
        self.Price=pd.DataFrame()
        self.Cap=pd.DataFrame()
        self.Index_weight=pd.DataFrame()
        self.Suspend=pd.DataFrame()
        self.flag=renewal_flag
        self.re_date=renewal_date
        self.day_lag=day_lag
        self.time_span=(None,None)
        self.ind_mapping=pd.Series()
        warnings.simplefilter(action = "ignore", category = RuntimeWarning)   
    def __call__(self,factor_path,ind_path,ind_level,price_path,cap_path,index_weight_path,ind_mapping_flag=True,**kwarg):
        '''
        run preprocessing
        
        factor_path: path to store factor file
        ind_path: path to store industry file
        ind_level: industry level
        price_path: path to store price file
        cap_path: path to store capitalization file  
        index_weight_path: path to store index weight file
        ind_mapping_flag: to transform industry as int during computing to accelerate. Not needed for int stored industry.
        '''
        t0=tm.time()
        print('\n\n--------------------[ Preprocess Start ]--------------------')
        self.change_flag(**kwarg)
        self.set_time(**kwarg)
        self.read_factor(path=factor_path,**kwarg)
        self.read_industry(path=ind_path,level=ind_level)
        if ind_mapping_flag:
            self.industry_mapping()
        self.read_price(path=price_path)
        self.read_cap(path=cap_path)
        self.read_index_weight(path=index_weight_path)
        D=self.integrate(ind_mapping_flag=ind_mapping_flag,**kwarg)
        t1=tm.time()        
        print('total time: %.3f s'%(t1-t0))
        print('--------------------[ Preprocess End ]--------------------\n')
        return D
    def change_flag(self,flag=None,renewal_date=None,day_lag=None,**kwarg):
        '''
        change renewal period
        '''
        if (flag is not None) and (flag not in ('monthly','daily')):
            raise Exception('flag must be "monthly" or "daily"')
        self.flag=(flag if flag is not None else self.flag)
        self.re_date=(renewal_date if renewal_date is not None else self.re_date)
        self.day_lag=(day_lag if day_lag is not None else self.day_lag)
    def set_time(self,start_time=None,end_time=None,**kwarg):
        '''  
        set time span
        '''
        start_time_tmp=(datetime.strptime(str(start_time),'%Y%m%d') if start_time is not None else None)
        end_time_tmp=(datetime.strptime(str(end_time),'%Y%m%d') if end_time is not None else None)
        self.time_span=(start_time_tmp,end_time_tmp)
        
    def read_factor(self,path,sub_factor=None,**kwarg):
        '''        
        factor file name: "xxx_yyyymmdd.csv"  where "yyyymmdd "should be continuous trading date. 
        factor file contains columns: StkID, dt(optional), ym(optional), factor_name1, factor_name2, ..
        
        path: root path where factor files are stored
        sub_factor: list of factor names to read in.
        '''   
        counts=0
        time_pool=[]
        for file_name in glob(path+'\*_*[0-9].csv'):         
            if self.flag=='monthly':
                time_oneday=datetime.strptime(global_func.split_time(file_name)[:6],'%Y%m')
                if time_oneday in time_pool:
                    continue
                else:
                    time_pool.append(time_oneday)
            else: #daily
                time_oneday=datetime.strptime(global_func.split_time(file_name),'%Y%m%d')
            time_oneday+=(timedelta(days=self.day_lag+1) if self.re_date is None else pd.tseries.offsets.DateOffset(months=1,days=self.re_date))
            factor_oneday=global_func.read_file_wrap(self.time_span,time_oneday,file_name)
            if (factor_oneday is None):
                continue
            all_factors=list(factor_oneday.columns)
            if 'StkID' in all_factors:
                all_factors.remove('StkID')

            if 'dt' in all_factors:
                all_factors.remove('dt')            
            elif 'ym' in all_factors:
                all_factors.remove('ym')
                
            if sub_factor is None:
                sub_factor=all_factors
            for factor_name in sub_factor:
                if factor_name not in all_factors:
                    continue                
                if factor_oneday[factor_name].isnull().all():
                    continue
                if factor_name not in self.dict.keys():
                    self.dict[factor_name]={}
                    self.dict[factor_name]['Factor']=pd.DataFrame()
                    self.dict[factor_name]['Time']=[]
                self.dict[factor_name]['Factor']=self.dict[factor_name]['Factor'].append(\
                                                pd.Series(data=factor_oneday[factor_name].values,\
                                                index=factor_oneday['StkID'].values,name=counts))
                self.dict[factor_name]['Time'].append(time_oneday)
            if counts%10==0:
                print('\r\tReading Factor \t '+str(time_oneday),end='\r')
            counts+=1
        for factor in self.dict.keys():
            self.dict[factor]['Factor'].index=range(len(self.dict[factor]['Time']))
        print('\r\tReading Factor      \t finished                 ')
                
    def read_industry(self,path,level):  
        '''       
        industry file name: "xxx_yyyymmdd.csv"  where "yyyymmdd "should be continuous trading date.
        industry file contains columns: StkID, industry_name1, industry_name2, ..
        
        path: root path where industry files are stored
        level: str, level_name
        '''
        counts=0
        for file_name in glob(path+'\*_*[0-9].csv'):                
            time_oneday=datetime.strptime(global_func.split_time(file_name),'%Y%m%d')
            industry_oneday=global_func.read_file_wrap(self.time_span,time_oneday,file_name)
            if industry_oneday is None:
                continue  
            self.Industry=self.Industry.append(pd.Series(data=industry_oneday[level].values, index= industry_oneday['StkID'].values,name=time_oneday))
            if counts%30==0:
                print('\r\tReading Industry \t '+str(time_oneday),end='\r')
            counts+=1
        print('\r\tReading Industry      \t finished                 ')
    def industry_mapping(self):
        '''
        mapping industry as int to accelerate.
        must set ind_mapping_flag in integrate if used
        '''
        ind_values=self.Industry.unstack().dropna().unique()
        ind_token=range(len(ind_values))
        self.ind_mapping=pd.Series(ind_token,index=ind_values)
        self.Industry=self.Industry.apply(lambda x: pd.Series(self.ind_mapping.reindex(x).values,index=x.index,name=x.name),axis=1)
      
    def read_price(self,path):
        '''
        market file name: "xxx_yyyymmdd.csv"  where "yyyymmdd "should be continuous trading date.
        market file contains columns: StkID, close, vwap, adjfactor, susp_days, maxupordown
        
        path: root path where industry files are stored
        '''
        counts=0
        for file_name in glob(path+'\*_*[0-9].csv'):
            time_oneday=datetime.strptime(global_func.split_time(file_name),'%Y%m%d')
            price_oneday=global_func.read_file_wrap(self.time_span,time_oneday,file_name)
            if price_oneday is None:
                continue
            vwap=price_oneday['vwap'].replace('None',np.nan).map(float)
            self.Price=self.Price.append(pd.Series(data= vwap.values*price_oneday['adjfactor'].values, index= price_oneday['StkID'].values,name=time_oneday))
            sus=pd.Series(data=0, index= price_oneday.iloc[:,0].values,name=time_oneday)
            sus.iloc[np.where((price_oneday['susp_days']!=0)|(price_oneday['maxupordown'])!=0)]=1
            self.Suspend=self.Suspend.append(sus)
            if counts%30==0:
                print('\r\tReading Price \t '+str(time_oneday),end='\r')
            counts+=1
        print('\r\tReading Price      \t finished                 ')
        
    def read_cap(self,path): 
        '''
        cap file name: "xxx_yyyymmdd.csv"  where "yyyymmdd "should be continuous trading date.
        market file contains columns: StkID, SRCap
        
        path: root path where industry files are stored
        '''
        counts=0
        for file_name in glob(path+'\*_*[0-9].csv'):
            time_oneday=datetime.strptime(global_func.split_time(file_name),'%Y%m%d')
            cap_oneday=global_func.read_file_wrap(self.time_span,time_oneday,file_name)
            if cap_oneday is None:
                continue
            self.Cap=self.Cap.append(pd.Series(data= cap_oneday['SRcap'].values, index= cap_oneday['StkID'],name=time_oneday))
            if counts%30==0:
                print('\r\tReading Capitalisation \t '+str(time_oneday),end='\r')
            counts+=1
        print('\r\tReading Capitalisation \t finished                 ')
            
    def read_index_weight(self,path):
        '''
        index weight file name: "xxx_yyyymmdd.csv"  where "yyyymmdd "should be continuous trading date.
        index weight file contains no column names with second column as "StkID" and fouth column as "Weight"
        
        path: root path where industry files are stored
        '''
        counts=0
        for file_name in glob(path+'\*_*[0-9].csv'):
            time_oneday=datetime.strptime(global_func.split_time(file_name),'%Y%m%d')         
            iw_oneday=global_func.read_file_wrap(self.time_span,time_oneday,file_name)
            if iw_oneday is None:
                continue
            self.Index_weight=self.Index_weight.append(pd.Series(data= iw_oneday.iloc[:,3].values, index= iw_oneday.iloc[:,1].values,name=time_oneday))
            if counts%30==0:
                print('\r\tReading InxWeight \t '+str(time_oneday),end='\r')
            counts+=1
        print('\r\tReading InxWeight      \t finished                 ')
        self.Index_weight=self.Index_weight.applymap(lambda x : np.nan if x=='None' else float(x)) # 存在 str 'None'
#    def set_factor_renewal_time(self,factor_name=None,time_list=None,**kwarg):        
#        if factor_name not in self.dict.keys():
#            raise Exception('Invalid factor_name')
#        if len(self.dict[factor_name]['Time'])!=len(time_list):
#            raise Exception('Invalid time_list')
#        self.dict[factor_name]['Time']=time_list        

    @staticmethod
    def integrate_mul(X):     
        '''
        align date time w/ different tables, used in integrate
        '''
        factor,Dict,Price,Suspend,Industry,Cap,Index_weight,ind_mapping,ind_mapping_flag=X[0],deepcopy(X[1]),deepcopy(X[2]),deepcopy(X[3]),deepcopy(X[4]),deepcopy(X[5]),deepcopy(X[6]),deepcopy(X[7]),X[8]
        if ind_mapping_flag and ind_mapping.shape[0]==0:
            raise Exception('set ind_mapping_flag as False if "ind_mapping" is not used')
        Dict['Return']=pd.DataFrame()
        counts=0
        for start,end in zip(Dict['Time'][:-1],Dict['Time'][1:]):
            if (start<Price.index[0]) or (end>Price.index[-1]) :
                Return_slice=pd.Series(0,index=Price.columns)
            else:
                while start not in Price.index:
                    start-=timedelta(days=1)
                while end not in Price.index:
                    end+=timedelta(days=1)
                Adjp_slice=Price[start:end]
                Return_slice=Adjp_slice.iloc[-1]/Adjp_slice.iloc[0]-1
            Dict['Return']=Dict['Return'].append(Return_slice.rename(counts))
            counts+=1        
        multiple_slice=Price[Dict['Time'][0]:Dict['Time'][-1]]            
        Dict['Multiple']=pd.DataFrame(data=(multiple_slice.iloc[1:].values/multiple_slice.iloc[:-1].values),index=multiple_slice.iloc[:-1].index,columns=multiple_slice.columns)
        Dict['Suspend']=Suspend[Dict['Time'][0]:Dict['Time'][-1]]    
        Dict['Time']=Dict['Time'][:-1]
        Dict['Factor'].drop(len(Dict['Time']),axis=0,inplace=True)        
        Dict['Industry']=pd.DataFrame()
        for counts in range(len(Dict['Time'])):
            time=Dict['Time'][counts]
            if time<Industry.index[0]:
                time=Industry.index[0]
            while time not in Industry.index:
                time-=timedelta(days=1)
            Dict['Industry']=Dict['Industry'].append(Industry.loc[time].rename(counts))
        if ind_mapping_flag:
            ind_mapping_reverse=pd.Series(data=ind_mapping.index,index=ind_mapping.values)
            Dict['Industry']=Dict['Industry'].apply(lambda x: pd.Series(ind_mapping_reverse.reindex(x).values,index=x.index,name=x.name),axis=1)
        Dict['Stock_Weight']=pd.DataFrame()
        for counts in range(len(Dict['Time'])):
            time=Dict['Time'][counts]
            if time<Cap.index[0]:
                time=Cap.index[0]               
            while time not in Cap.index:
                time-=timedelta(days=1)
            Dict['Stock_Weight']=Dict['Stock_Weight'].append(Cap.loc[time].rename(counts))           
        Dict['Industry_Weight']=pd.DataFrame()
        for counts in range(len(Dict['Time'])):
            time=Dict['Time'][counts]
            if time<Index_weight.index[0]:
                time=Index_weight.index[0] 
            while time not in Index_weight.index:
                time-=timedelta(days=1)
            industry_weight=pd.concat([Index_weight.loc[time].rename('weight'),Dict['Industry'].iloc[counts].rename('industry')],axis=1).dropna(axis=0).groupby('industry').aggregate(sum)['weight']
            Dict['Industry_Weight']=Dict['Industry_Weight'].append(industry_weight.rename(counts)) 
        return (factor,Dict)
        
    def integrate(self,processors=None,ind_mapping_flag=False,**kwarg):
        '''
        integrate w/ multiprocessing 
        align date time after reading everything
        
        processors: number of processors to use
        ind_mapping_flag: whether used industry_mapping function
        '''
        print('\r\tIntegrate           \t start     ',end='\r')
        Suspend=self.Suspend.apply(global_func.pre_sus)
        X=[[factor,deepcopy(self.dict[factor]),self.Price,Suspend,self.Industry,self.Cap,self.Index_weight,self.ind_mapping,ind_mapping_flag] for factor in self.dict.keys()]
                   
        pool = Pool(processes=processors)
        multi_res=pool.map(self.integrate_mul, X)
        
        Dict={res[0]:res[1] for res in multi_res}
        print('\r\tIntegrate           \t finished     ')        
        return Dict 