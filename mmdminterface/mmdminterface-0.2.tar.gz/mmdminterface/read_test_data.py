#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xlrd
f_xp='xxx/test_case_data.xls'
table_config= xlrd.open_workbook(f_xp).sheet_by_name('config')
base_url=[]
for k in range(1,table_config.ncols):
    base_url.append(table_config.cell_value(1,k))
table_cases=xlrd.open_workbook(f_xp).sheet_by_name('case')
nrows=table_cases.nrows
ncols=table_config.ncols

def read_case():
    case_data=[]
    try:
        for i in range(1,nrows):
            case = {}
            case['case_name']=table_cases.cell_value(i,0)
            case['method']=table_cases.cell_value(i,1)
            if 'BU_' in table_cases.cell_value(i,2):
                rep=table_cases.cell_value(i,2)[0:4]
                case['url']=table_cases.cell_value(i,2).replace(rep,base_url[int(rep[3:4])-1])
            else:
                case['url'] = table_cases.cell_value(i, 2)
            case['params']=table_cases.cell_value(i,3)
            case['data']=table_cases.cell_value(i,4)
            case['expectation']=table_cases.cell_value(i,5)
            case['Preconditions']=table_cases.cell_value(i,6)
            case['get_params']=table_cases.cell_value(i,7)
            case_data.append(case)
        return case_data

    except:
        print('测试用例异常')

def read_db_config():
    db_config = {'host': '', 'user': '', 'passwd': '', 'port': '', 'db': ''}
    try:
        db_config['host'] = table_config.cell_value(7, 1)
        db_config['user'] = table_config.cell_value(8, 1)
        db_config['passwd'] = table_config.cell_value(9, 1)
        db_config['port'] = int(table_config.cell_value(10, 1))
        db_config['db'] = table_config.cell_value(11, 1)
        return db_config

    except:
        print('配置数据异常1')

def read_user_config():
    user_config = {'login_url': '', 'loginBy': '', 'password': ''}
    try:
        user_config['login_url'] =table_config.cell_value(3, 1)
        user_config['loginBy'] = table_config.cell_value(4, 1)
        user_config['password'] = table_config.cell_value(5, 1)
        return user_config

    except:
        print('配置数据异常2')

def read_shh_config():
    ssh_config = {'ssh_host': '', 'ssh_port': '', 'keyfile': '', 'ssh_user': ''}
    try:
        ssh_config['ssh_host'] = table_config.cell_value(13, 1)
        ssh_config['ssh_port'] = int(table_config.cell_value(14, 1))
        ssh_config['keyfile'] = table_config.cell_value(15, 1)
        ssh_config['ssh_user'] = table_config.cell_value(16, 1)

        return ssh_config

    except:
        print('配置数据异常3')
