#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, time, unittest, sys
from Laputa import HTMLTestRunner


def Get_Html(test_class, basedir):
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_class))
    now = time.strftime('%Y-%m-%d %I_%M_%S_%p')
    file_dir = os.path.join(basedir, 'report/history_report')
    file = os.path.join(file_dir, (now + '.html'))
    re_open = open(file, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=re_open, title='接口测试报告', description='测试结果')
    runner.run(suite)
    last_report = os.path.join(os.path.join(basedir, 'report/last_report'), 'last_report.html')
    with open(last_report, "wb") as nf, open(file, "rb") as of:
        nf.write(of.read())


def run():
    unittest.main(warnings='ignore')
