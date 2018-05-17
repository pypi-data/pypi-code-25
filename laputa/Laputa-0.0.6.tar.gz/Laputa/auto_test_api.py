#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from requests import Request,Session
import unittest
from mmdminterface import read_test_data,ddt
global case_date
case_date=[]

@ddt.ddt
class Interface(unittest.TestCase):

    def __init__(self,f_xP, methodName='runTest'):
        """Create an instance of the class that will use the named test
           method when executed. Raises a ValueError if the instance does
           not have a method with the specified name.
        """'/Users/mckay/JMeter/minterface/examples/demo2/test_data/test_case_data.xls'
        self._testMethodName = methodName
        self._outcome = None
        self._testMethodDoc = 'No test'
        try:
            testMethod = getattr(self, methodName)
        except AttributeError:
            if methodName != 'runTest':
                # we allow instantiation with no explicit method name
                # but not an *incorrect* or missing method name
                raise ValueError("no such test method in %s: %s" %
                      (self.__class__, methodName))
        else:
            self._testMethodDoc = testMethod.__doc__
        self._cleanups = []
        self._subtest = None

        # Map types to custom assertEqual functions that will compare
        # instances of said type in more detail to generate a more useful
        # error message.
        self._type_equality_funcs = {}
        self.addTypeEqualityFunc(dict, 'assertDictEqual')
        self.addTypeEqualityFunc(list, 'assertListEqual')
        self.addTypeEqualityFunc(tuple, 'assertTupleEqual')
        self.addTypeEqualityFunc(set, 'assertSetEqual')
        self.addTypeEqualityFunc(frozenset, 'assertSetEqual')
        self.addTypeEqualityFunc(str, 'assertMultiLineEqual')
        self.case_date = read_test_data.ReadExcel(f_xP).read_case()


    def setUp(self):
        self.new_case_date =self.case_date
        self.reponses={}

    def rep_params(self, case_date):
        reps=re.compile('(\$\{.*\})')
        keys=reps.findall(case_date)
        for key in keys:
            case_date=case_date.replace(key,self.reponses[key])
        return case_date

    def get_params(self,text,rule):
        rep = re.compile(rule)
        return rep.findall(text)[0]

    def get_req(self,case_date):
        if '$' in case_date['url']:
            case_date['url']=self.rep_params(case_date['url'])
        if case_date['params']!='':
            return Request(case_date['method'], case_date['url'], params=eval(case_date['params']))
        elif case_date['data']!='':
            if '$' in case_date['data']:
                case_date['data'] = self.rep_params(case_date['data'])
            return Request(case_date['method'], case_date['url'], json=eval(case_date['data']))
        else:
            return Request(case_date['method'], case_date['url'])

    @ddt.data(*case_date)
    def test(self, case_date):
        case = [int(x) for x in case_date['Preconditions'].split(',')]
        session=Session()
        for i in case:
            req =self.get_req(self.new_case_date[i-1])
            prepped = session.prepare_request(req)
            sent = session.send(prepped)
            self.assertEqual(sent.status_code,200)
            self.assertTrue(self.new_case_date[i - 1]['expectation'] in str(sent.text))
            if self.new_case_date[i-1]['get_params']!='':
                print(self.new_case_date[i-1]['get_params'])
                dict_case_date=eval(self.new_case_date[i - 1]['get_params'])
                for key in dict_case_date.keys():
                    self.reponses[key]=self.get_params(sent.text,dict_case_date[key])


    def tearDown(self):
        pass

if __name__=='__main__':

    cc=Interface('/Users/mckay/JMeter/minterface/examples/demo2/test_data/test_case_data.xls')


