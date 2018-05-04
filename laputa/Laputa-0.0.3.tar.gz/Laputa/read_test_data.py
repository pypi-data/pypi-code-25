#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xlrd, os

basedir = os.path.abspath(os.path.dirname(__file__))


class ReadExcel():
    def __init__(self, f_xp):
        self.table_config = xlrd.open_workbook(f_xp).sheet_by_name('config')
        self.base_url = []
        for k in range(1, self.table_config.ncols):
            self.base_url.append(self.table_config.cell_value(1, k))
        self.table_cases = xlrd.open_workbook(f_xp).sheet_by_name('case')
        self.nrows = self.table_cases.nrows
        self.ncols = self.table_config.ncols

    def read_case(self):
        case_data = []
        try:
            for i in range(1, self.nrows):
                case = {}
                case['case_name'] = self.table_cases.cell_value(i, 0)
                case['method'] = self.table_cases.cell_value(i, 1)
                if 'BU_' in self.table_cases.cell_value(i, 2):
                    rep = self.table_cases.cell_value(i, 2)[0:4]
                    case['url'] = self.table_cases.cell_value(i, 2).replace(rep, self.base_url[int(rep[3:4]) - 1])
                else:
                    case['url'] = self.table_cases.cell_value(i, 2)
                case['params'] = self.table_cases.cell_value(i, 3)
                case['data'] = self.table_cases.cell_value(i, 4)
                case['expectation'] = self.table_cases.cell_value(i, 5)
                case['Preconditions'] = self.table_cases.cell_value(i, 6)
                case['get_params'] = self.table_cases.cell_value(i, 7)
                case_data.append(case)

            with  open(basedir + '/test_cases.txt', 'w') as f:
                f.write(str(case_data))
            return case_data

        except:
            print('测试用例异常')

    def read_db_config(self):
        db_config = {'host': '', 'user': '', 'passwd': '', 'port': '', 'db': ''}
        try:
            db_config['host'] = self.table_config.cell_value(7, 1)
            db_config['user'] = self.table_config.cell_value(8, 1)
            db_config['passwd'] = self.table_config.cell_value(9, 1)
            db_config['port'] = int(self.table_config.cell_value(10, 1))
            db_config['db'] = self.table_config.cell_value(11, 1)
            return db_config

        except:
            print('配置数据异常1')

    def read_user_config(self):
        user_config = {'login_url': '', 'loginBy': '', 'password': ''}
        try:
            user_config['login_url'] = self.table_config.cell_value(3, 1)
            user_config['loginBy'] = self.table_config.cell_value(4, 1)
            user_config['password'] = self.table_config.cell_value(5, 1)
            return user_config

        except:
            print('配置数据异常2')

    def read_shh_config(self):
        ssh_config = {'ssh_host': '', 'ssh_port': '', 'keyfile': '', 'ssh_user': ''}
        try:
            ssh_config['ssh_host'] = self.table_config.cell_value(13, 1)
            ssh_config['ssh_port'] = int(self.table_config.cell_value(14, 1))
            ssh_config['keyfile'] = self.table_config.cell_value(15, 1)
            ssh_config['ssh_user'] = self.table_config.cell_value(16, 1)

            return ssh_config

        except:
            print('配置数据异常3')


