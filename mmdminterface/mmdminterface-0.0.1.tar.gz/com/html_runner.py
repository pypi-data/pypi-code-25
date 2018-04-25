#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,time,unittest,sys
pathname = os.getcwd()
sys.path.append(pathname)
from mmdminterface import HTMLTestRunner
def Html_Runner(test_cases):
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_cases))
    now = time.strftime('%Y-%m-%d %I_%M_%S_%p')
    basedir = os.path.abspath(os.path.dirname(__file__))
    file_dir = os.path.join(basedir, 'report/history_report')
    file = os.path.join(file_dir, (now + '.html'))
    re_open = open(file, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=re_open, title='接口测试报告', description='测试结果')
    runner.run(suite)
    last_report = os.path.join(os.path.join(basedir, 'report/last_report'),'last_report.html')
    with open(last_report, "wb") as nf, open(file, "rb") as of:
        nf.write(of.read())