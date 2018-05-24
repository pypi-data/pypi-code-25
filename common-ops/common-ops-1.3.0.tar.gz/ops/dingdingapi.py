#! /usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import requests
import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

## not use
class Get(object):
    def __init__(self, name):
        self.name = name
    def GetProcess(self, url, n, headers=None, cookies=None, debug=None):
        MinSpan = 100.000
        MaxSpan = 0.000
        sumSpan = 0.000
        over1s = 0
        for i in range(n):
            startTime = datetime.now()
            try:
                res = requests.get(url, timeout=1000000, headers=headers, cookies=cookies)
                global ResponseData
                ResponseData = res.text
                self.ResponseData = ResponseData
                print(u'ResponseData:\n' + ResponseData)
            except:
                pass
            endTime = datetime.now()
            span = (endTime - startTime).total_seconds()
            sumSpan = sumSpan + span
            if span < MinSpan:
                MinSpan = span
            if span > MaxSpan:
                MaxSpan = span
            #超过1秒的
            if span > 1:
                over1s = over1s + 1
            span_ms = span*1000
            self.ResponseTime = span_ms
            print(u'GET  %s\n Spent: %s seconds\n' % (url, span))
        print(u'\n  =================SummaryReport=================\n  \Requested:%s Times\n  Total Spent:%ss\n  Avg:%ss\n  Max:%ss\n  Min:%ss\n  Over 1 seconds:%stime '\
            %(n,sumSpan,sumSpan/n,MaxSpan,MinSpan,over1s))
        print('  =================SummaryReport=================')


class Post(object):
    def __init__(self, name):
        self.name = name
        self.casenumber = 0
        self.ExpressionResult = []
        self.url = None
        self.n = None
        self.csv = None
        self.assertcsv = None
        self.body = None
        self.assertbody = None
        self.extractor = None
    def PostProcess(self, url, n=1, csv=None, assertcsv=None, body=None, assertbody=None, extractor=None, headers=None, debug=None):
    #url-地址,n-循环次数,csv-参数文件,assertcsv-断言文件,body-自定义参数,assertbody-自定义断言,extractor-提取器,headers-头,debug-打印更多debug信息
        self.casenumber += n
        self.url = url
        self.n = n
        self.csv = csv
        self.assertcsv = assertcsv
        self.body = body
        self.assertbody = assertbody
        self.extractor = extractor
        self.headers = headers

        MinSpan = 10.000
        MaxSpan = 0.000
        sumSpan = 0.000
        passNum = 0.00
        float(passNum)
        failNum = 0.00
        float(failNum)
        over1s = 0

        #检查错误函数
        def test_fail():
            if failNum > 0:
                print('\033[1;31;40m')
                raise Exception("test fail!!!")
                print('\033[0m')
            else:
                pass

       #提取器处理-extractor-解析参数名和表达式
        if extractor:
            ReferenceName = extractor[0]
            RegularExpression = extractor[1]
        else:
            pass

        #定义提取函数
        def func_extractor():
            if extractor:
                val = re.findall(unicode(RegularExpression), PostResponseData, re.I)
                if val:
                    self.ExpressionResult = [ReferenceName, val]
                else:
                    print('Expression Error!')
                    self.ExpressionResult = [ReferenceName, ['error!!!',]]
            else:
                pass
            return (self.ExpressionResult)

        #根据提供的参数确认分支
        if csv == None and extractor != None:
            jsdata = body ## 留着备用,处理body
            startTime = datetime.now()
            try:
                if body != None:
                    print('post请求')
                    res = requests.post(url, jsdata, headers=headers, timeout=1000000)
                    print('ResponseCode: '),(res.status_code)
                else:
                    print('get请求')
                    res = requests.get(url, timeout=1000000, headers=headers)
                    print('ResponseCode: '),(res.status_code)
                PostResponseData = res.text
                self.ResponseData = PostResponseData

                # 提取函数
                func_extractor()

                # 断言
                if assertbody != None:
                    resval = re.search(unicode(assertbody), PostResponseData, re.I)
                    if resval:
                        passNum += 1
                    else:
                        failNum += 1
                        print(u'AssertError! not contain[%s]') % (unicode(assertbody))
                        print(u'\nPOST  %s\nBody  %s\n ' % (url, jsdata)) #debug
                        print(u'ResponseCode: ') #debug
                        print(res.status_code) #debug
                        print(u'\nResponseData:\n' + PostResponseData) #debug
                if debug:
                    print(u'\nPOST  %s\nBody  %s\n ' % (url, jsdata)) #debug
                    print(u'ResponseCode: ') #debug
                    print(res.status_code) #debug
                    print(u'\nResponseData:\n' + PostResponseData) #debug
                else:
                    pass
            except:
                pass

            endTime = datetime.now()
            span = (endTime - startTime).total_seconds()
            sumSpan = sumSpan + span
            if span < MinSpan:
                MinSpan = span
            else:
                pass
            if span > MaxSpan:
                MaxSpan = span
            else:
                pass
            #超过1秒的
            if span > 1:
                over1s = over1s + 1
            else:
                pass
            span_ms = span*1000
            self.ResponseTime = span_ms

            print(u'Spent: %s seconds\n' % (span))
            test_fail()
        elif csv == None and extractor == None:
            #正常普通请求,有断言分支
            jsdata = body
            startTime = datetime.now()
            if body != None:
                print('post请求')
                res = requests.post(url, jsdata, headers=headers, timeout=1000000)
                print('ResponseCode: '),(res.status_code)
            else:
                print('get请求')
                res = requests.get(url, timeout=1000000, headers=headers)
                print('ResponseCode: '),(res.status_code)
            PostResponseData = res.text
            self.ResponseData = PostResponseData

            # 断言
            if assertbody != None:
                resval = re.search(unicode(assertbody), PostResponseData, re.I)
                if resval:
                    passNum += 1
                else:
                    failNum += 1
                    print(u'AssertError! not contain[%s]') % (unicode(assertbody))
                    print(u'\nGET/POST  %s\nBody  %s\n ' % (url, jsdata))
                    print(u'ResponseCode: ')
                    print(res.status_code)
                    print(u'\nResponseData:\n' + PostResponseData)
            if debug:
                print(u'\nGET/POST  %s\nBody  %s\n ' % (url, jsdata))
                print(u'ResponseCode: ')
                print(res.status_code)
                print(u'\nResponseData:\n' + PostResponseData)
            else:
                pass

            endTime = datetime.now()
            span = (endTime - startTime).total_seconds()
            sumSpan = sumSpan + span
            if span < MinSpan:
                MinSpan = span
            else:
                pass
            if span > MaxSpan:
                MaxSpan = span
            else:
                pass
            #超过1秒的
            if span > 1:
                over1s = over1s + 1
            else:
                pass
            span_ms = span*1000
            self.ResponseTime = span_ms

            print(u'Spent: %s seconds\n' % (span))
            test_fail()
        elif csv != None and assertcsv == None:
            csvlist = []
            try:
                with open(csv, 'rb') as f:
                    for body in f.readlines():
                        csvlist.append(body.strip('\r\n').strip('\n'))
            except:
                print('open csv error!')
            finally:
                f.close()
            for i in range(n):
                startTime = datetime.now()
                jsdata = csvlist[i]
                try:
                    res = requests.post(url, jsdata, timeout=1000000, headers=headers)
                    PostResponseData = res.text
                    self.ResponseData = PostResponseData
                    print(i + 1)
                    print(u'\nPOST  %s\nBody  %s\n ' % (url, jsdata))
                    print(u'ResponseCode: ')
                    print(res.status_code)
                    print(u'ResponseData:\n' + PostResponseData)
                except:
                    failNum += 1
                    pass

                # 提取函数
                func_extractor()
                # 断言
                if assertbody != None:
                    resval = re.search(unicode(assertbody), PostResponseData, re.I)
                    if resval:
                        passNum += 1
                    else:
                        failNum += 1
                        print(u'AssertError! not contain[%s]') % (unicode(assertbody))
                        print(u'\nPOST  %s\nBody  %s\n ' % (url, jsdata)) #debug
                        print(u'ResponseCode: ') #debug
                        print(res.status_code) #debug
                        print(u'\nResponseData:\n' + PostResponseData) #debug

                endTime = datetime.now()
                span = (endTime - startTime).total_seconds()
                sumSpan = sumSpan + span
                if span < MinSpan:
                    MinSpan = span
                else:
                    pass
                if span > MaxSpan:
                    MaxSpan = span
                else:
                    pass
                #超过1秒的
                if span > 1:
                    over1s = over1s + 1
                else:
                    pass
                span_ms = span*1000
                self.ResponseTime = span_ms

                print(u'Spent: %s seconds\n' % (span))

            print(u'''\n  =================SummaryReport=================
  Requested:%s Times
  Total Spent:%ss
  Avg:%ss
  Max:%ss
  Min:%ss
  Over 1 seconds:%sHits
  Pass:%d
  Fail:%d
  Error:%.2f%%''' % (n, sumSpan, sumSpan/n, MaxSpan, MinSpan, over1s, passNum, failNum, failNum/n*100))
            print('  =================SummaryReport=================')
            test_fail()
        else:
            csvlist = []
            assertlist = []
            try:
                with open(csv, 'rb') as f, open(assertcsv, 'rb') as f2:
                    for body in f.readlines():
                        csvlist.append(body.strip('\r\n').strip('\n'))
                        assertlist.append(f2.readline().strip('\r\n').strip('\n'))
            except:
                print('open csv error!')
            finally:
                f.close()
            for i in range(n):
                if debug:
                    print('\n\nCASENO: ' + str(i + 1))
                else:
                    pass
                startTime = datetime.now()
                jsdata = csvlist[i]
                asdata = assertlist[i]
                try:
                    res = requests.post(url, jsdata, timeout=1000000, headers = headers)
                    PostResponseData = res.text
                    self.ResponseData = PostResponseData

                    # 提取函数
                    func_extractor()

                    #断言
                    resval = re.search(unicode(asdata), PostResponseData, re.I)
                    if resval:
                        passNum += 1
                    else:
                        failNum += 1
                        print(i + 1)
                        print(u'\nPOST  %s\nBody  %s ' % (url, jsdata))
                        print(u'ResponseCode: ')
                        print(res.status_code)
                        print(u'ResponseData:\n' + PostResponseData)
                        print(u'AssertError! not contain[%s]') % (unicode(asdata))
                    if debug:
                        print(u'\nGET/POST  %s\nBody  %s\n ' % (url, jsdata))
                        print(u'ResponseCode: ')
                        print(res.status_code)
                        print(u'\nResponseData:\n' + PostResponseData)
                    else:
                        pass
                except:
                    failNum += 1
                    pass
                
                endTime = datetime.now()
                span = (endTime - startTime).total_seconds()
                sumSpan = sumSpan + span
                if span < MinSpan:
                    MinSpan = span
                else:
                    pass
                if span > MaxSpan:
                    MaxSpan = span
                else:
                    pass
                #超过1秒的
                if span > 1:
                    over1s = over1s + 1
                else:
                    pass
                span_ms = span*1000
                self.ResponseTime = span_ms

                print(u'Spent: %s seconds\n'%(span)) #性能测试开启
            print(u'''\n  =================SummaryReport=================
  Requested:%s Times
  Total Spent:%ss
  Avg:%ss
  Max:%ss
  Min:%ss
  Over 1 seconds:%sHits
  Pass:%d
  Fail:%d
  Error:%.2f%%''' % (n, sumSpan, sumSpan/n, MaxSpan, MinSpan, over1s, passNum, failNum, failNum/n*100))
            print('  =================SummaryReport=================')
            test_fail()

class READ_FILE_DATA(object):
    def __init__(self, name):
        self.name = name
        self.data = []
    def filedata(self, propath, filepath, debug=None):
            fullpath = os.path.join(propath, filepath)
            with open(fullpath, 'rb') as f:
                for line in f.readlines():
                    self.data.append(line.replace('\r\n','').replace('\n',''))
                    if debug:
                        print('READ_FILE_DATA - ',line)
                    else:
                        pass