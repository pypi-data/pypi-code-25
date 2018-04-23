#-*- coding:utf-8 -*-
import sys,json,datetime,copy
import pandas as pd

if sys.version[0]=='2':
    from exceptions import Exception
    from urllib import urlopen
if sys.version[0]=='3':
    from urllib.request import urlopen

from FuturesCode import *


# 获取指定品种数据
def get_daily_data(instrumentid,data_type=None, start_date=None, end_date=None,verbose=False):
    '''
    :param instrumentid: Str type, the code of the trading future
    :param data_type: a list of str,this func will get open,high,low,close and volume data by default if no value is assigned to this parameter
    :param start_date: Str type, start date of the dataset,"Y-m-d"
    :param end_date:Str type, end date of the dataset,"Y-m-d"
    :param verbose: Bool type, if verbose is true,then print out the according message
    :return:a pandas dataframe of the target future daily candle data.
    '''

    # 输入参数检测  Input Detection
    if instrumentid.upper() not in CN_All_Futures:
        raise ("Error instrument code name")

    if data_type:
        for dtype in data_type:
            if dtype not in ['close', 'open', 'high', 'low', 'volume']:
                raise Exception(
                    "Error data type! Data type must be one of these values:'close','open','high','low','volume'")

    yesterday = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')

    if start_date != None:  # or end_date!=None:
        if start_date > yesterday:  # or end_date>yesterday:
            raise Exception("start_date must be less than or equal to yesterday when getting a daily history data")

    if end_date != None:
        if end_date > yesterday:
            raise Exception("end_date must be less than or equal to yesterday when getting a daily history data")

    if start_date != None and end_date != None:
        if start_date > end_date:
            raise Exception("start_date must be earlier then end_date")

    url = "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol=" + instrumentid.upper() + "0"  # +"RB0"   #网址
    # 打开网页链接  open the website
    wp = urlopen(url)

    if verbose:
        print ("getting " + instrumentid + " data")
    # 读取网页数据  read the content of the website
    if sys.version[0] == '2':
        jasoncontent = wp.read()
    elif sys.version[0] == '3':
        jasoncontent = wp.read().decode()  # change byte type into str type

    # 如果没有取到数据   if not get raw data
    if jasoncontent == 'null':
        print("something occured when getting the " + instrumentid.lower() + " data,please try again")
        return None

    pycontent = json.loads(jasoncontent)  # json数据格式转换
    data = pd.DataFrame(pycontent, columns=['date', 'open', 'high', 'low', 'close',
                                            'volume'])  # 转换成dataframe   change web data into dataframe
    data = data.set_index('date')
    data = data.astype('float32')

    # 获取对应data_type数据
    if data_type == None:
        target_data = data
    else:
        target_data = data[data_type]

    # 获取对应日期数据
    if start_date != None and end_date == None:
        target_data = target_data[target_data.index >= start_date]

    elif start_date == None and end_date != None:
        target_data = target_data[target_data.index <= end_date]

    elif start_date != None and end_date != None:
        target_data = target_data[target_data.index >= start_date]
        target_data = target_data[target_data.index <= end_date]

    return target_data


#获取所有品种数据,长度一致
def get_all_daily_data(same_length=False,verbose=False):
    '''
    :param same_length: 设置返回是否为长度一致的数据，如为True，则所有品种的数据长度一致
    :param verbose: 如果verbose设置成true,输出数据获取信息
    :return:  根据设置获取所有品种日线数据
    '''
    if same_length!=False and same_length!=True:
        raise  Exception("error input,same_length should be BOOL TYPE")

    data_dict=copy.deepcopy(CN_All_Futures)
    min_length=None
    for instrument_id in CN_All_Futures:
        temp_data = get_daily_data(instrument_id,verbose=verbose)
        if min_length == None:
            min_length = len(temp_data)
        if min_length > len(temp_data):
            min_length = len(temp_data)
    if same_length:
        for instrument_id in CN_All_Futures:
            data_dict[instrument_id]=data_dict[instrument_id][-min_length:]
    return data_dict

