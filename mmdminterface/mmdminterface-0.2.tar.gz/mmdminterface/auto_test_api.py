#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from requests import Request,Session
import unittest
from mmdminterface import read_test_data,ddt
user_config=read_test_data.read_user_config()
case_date= read_test_data.read_case()
new_case_date=case_date

@ddt.ddt
class Interface(unittest.TestCase):

    def setUp(self):
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
            req =self.get_req(new_case_date[i-1])
            prepped = session.prepare_request(req)
            sent = session.send(prepped)
            self.assertEqual(sent.status_code,200)
            self.assertTrue(new_case_date[i - 1]['expectation'] in str(sent.text))
            if new_case_date[i-1]['get_params']!='':
                print(new_case_date[i-1]['get_params'])
                dict_case_date=eval(new_case_date[i - 1]['get_params'])
                for key in dict_case_date.keys():
                    self.reponses[key]=self.get_params(sent.text,dict_case_date[key])


    def tearDown(self):
        pass

if __name__=='__main__':
    unittest.main()
