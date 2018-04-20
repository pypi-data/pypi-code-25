# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 22:01:21 2018

@author: jasonai
"""
import os
import sys
import requests
import numpy as np
import pandas as pd
from pmipy import pmi
from random import choice
from threading import Thread

gd_url = 'http://restapi.amap.com/v3/geocode/geo?' #高德地理编码api服务地址

keys_list = ['f2028746f4fe36d6b665d626b9481e73', 'd915aa691a88cdb29fe18f120feea269', 
'9ee6aa4c8210ff9d8134a16d5d216053','1a7169154454db57564bd1639d849dcb',
'7a6c90d70d50f22d942928d1ffd25d8a','b77b9f05cdb10aac5b5061e31cd24254',
'8b55981ffe68fed09b3299118955b317','2c603a0aa3f9ac69afe468cd8cebfda5',]

def gd_geocode(address): #根据地址获取高德经纬度后转化为百度经纬度\
    # 解决高德API日访问次数限制问题
    key = choice(keys_list)
    gd_parm1 = {'key': key, 'address': address, 'city': '',} #高德key
    try:
        response = requests.get(url=gd_url, params=gd_parm1, timeout=10).json()
        if response['status'] == '1':
            # 获取第一个返回地址信息
            geocode = response['geocodes'][0]
            lng = float(geocode['location'].split(',')[0])
            lat = float(geocode['location'].split(',')[1])
            f_address = geocode['formatted_address']
            province = geocode['province']
            city = geocode['city']
            district = geocode['district']
            level = geocode['level']
            result = [lng, lat, f_address, province, city, district, level]
        else:
            result = ['请求失败','','','','','','']
    except:
        result = ['网络无响应','','','','','','']

    return result

def run_thread(df, adr_search):
    res_list = []
    for adr in df[adr_search.split('-')].sum(axis=1):
        res_list.append(gd_geocode(adr))
    df2 = pd.DataFrame(res_list,columns=['经度','纬度','返回地址','省','市','区','地址类型'],index=df.index)
    # df[['new1', 'new2', 'new3', 'new4','new5', 'new6','new7']] = df.apply(gd_geocode)
    return pd.concat([df,df2],axis=1)

# 多线程
class MyThread(Thread):
    def __init__(self, df, adr_search):
        Thread.__init__(self)
        self.df = df
        self.adr_search = adr_search

    def run(self):
        self.result = run_thread(self.df, self.adr_search)

    def get_result(self):
        return self.result

@pmi.execInfo()
def getTargetCoordinate(filepath, adr_search, thread=20, target_coordinate='gaode',file_ouput=''):
    path = os.path.split(filepath)[0]
    filename = os.path.splitext(os.path.split(filepath)[1])[0]
    filesuffix = os.path.splitext(os.path.split(filepath)[1])[1]
    # 读取文件
    if filesuffix == '.csv':
        df = pd.read_csv(filepath, engine='python')
    elif filesuffix == '.xlsx':
        df = pd.read_excel(filepath)
    else:
        sys.exit('Please input csv or xlsx file!')
    
    try:
        thread = int(thread)
    except ValueError:
        sys.exit('请输入正确的线程数(整数值)！')
    df = df.head(100)
    # 如果线程数小于数据框长度的1/2
    if thread < len(df) / 2:
        df_split = np.array_split(df, thread)
    else:
        df_split = np.array_split(df, 20)

    # 构建多线程
    thd_list = []
    for df in df_split:
        thd = MyThread(df, adr_search)
        thd.start()
        thd_list.append(thd)
    
    for t in thd_list: # 等待所有线程执行完毕
        t.join()
    
    res_list = []
    for t in thd_list:
        res = t.get_result()
        print(t.get_result())
        res_list.append(res)
    
    df_res = pd.concat(res_list)
    
    if target_coordinate == 'baidu':
        print('正在开发...')
    if file_ouput:
        filename = file_ouput
    outfile = filename + '_' + target_coordinate + '坐标.xlsx'
    df_res.to_excel(os.path.join(path, outfile), index=False)

if __name__ == '__main__':
    filepath = r'E:\CloudStation\康饮商圈分析\零售饮料\江苏省linxdata_经纬度匹配最终版V1.xlsx'
    adr_search = '省份-城市名称-附近标志'

    getTargetCoordinate(filepath, adr_search)
    