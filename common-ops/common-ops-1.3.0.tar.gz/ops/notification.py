#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 07/02/2018 15:33
# @Author  : Liozza
# @Site    : 
# @File    : notification
# @Software: PyCharm

import urllib2
import json
import datetime
from dingdingapi import *


class Notification(object):
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Lambda Function'
        }

    def msteams_send_msg(self, channel, service, status, color='#FF9999'):
        """
            send message to microsoft teams
            :param status: 
            :param service: 
            :param color: 
            :param channel: which channel you want to send
        """
        section = [{
            'facts': [
                {
                    "name": "Date",
                    "value": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                {
                    "name": "Service",
                    "value": service
                },
                {
                    "name": "Status",
                    "value": status
                }
            ]
        }]
        content = {
                    '@type': 'MessageCard',
                    '@context': 'http://schema.org/extensions',
                    'themeColor': color,
                    'text': '**#[WANRING] Suspicious Service#**',
                    'sections': section
                   }
        send_channel = channel
        request = urllib2.Request(url=send_channel, data=json.dumps(content), headers=self.headers)
        response = urllib2.urlopen(request).read()
        print response

    @staticmethod
    def dingtalk_send_msg(message, tomans):

        # jenkins path process
        # propath = os.getcwd()
        # if 'jenkins' in propath:
        #     propath = os.path.join(propath, 'searchapi/other_scripts')
        # else:
        #     pass
        # total = 0
        # environment
        headers = {'Content-Type': 'application/json'}
        debug = 'true'
        # ===========================init done

        # # get access token
        sample = Post('openapi')
        url = 'https://oapi.dingtalk.com/gettoken?corpid=ding53af0b7d2c24704535c2f4657eb6378f&corpsecret=Bhfb8P5z75WrvRQ_WAUJcq88seOOjb_LiRTT8ki-qnejp-ryKrkbgd6VxsLVoYaT'
        sample.PostProcess(url=url, extractor=['access_token', '"access_token":[\s]*"(.*?)"'])
        access_token = sample.ExpressionResult[1][0]

        deptId = '29464045'
        namelist = tomans.split(',')
        # get department user list
        url = 'https://oapi.dingtalk.com/user/simplelist?access_token=' + access_token + '&department_id=' + deptId
        sample.PostProcess(url=url)
        global ResponseData
        ResponseData = sample.ResponseData

        # get user id
        def name2id(x):
            global ResponseData
            RegularExpression = '\"name\":\"' + x + '\",\"userid\":\"(.*?)\"'
            print RegularExpression
            val = re.findall(RegularExpression, ResponseData)
            if val:
                id = val[0]
            else:
                print id + u"没有这个用户，请联系管理员添加这个用户"
            return id

        touser = ''
        for name in namelist:
            id = name2id(name)
            touser = touser + id + '|'
        print touser

        url = 'https://oapi.dingtalk.com/message/send?access_token=' + access_token
        body = '{"touser": "' + touser + '","agentid": "77216311","msgtype": "text","text": {"content":"' + message + '"}}'
        print body
        # # body = '{"toparty": "-1","agentid": "77216311","msgtype": "text","text": {"content":"' + JOB_NAME + '  ' + BUILD_NUMBER + '  编译完成"}}'
        sample.PostProcess(url=url, body=body, headers=headers)
        print sample.ResponseData

# if __name__ == '__main__':
    # to_channel = 'https://outlook.office.com/webhook/0b430963-d538-47e0-aa80-806b8a8917bc@cbe05c41-29ee-44bb-8167' \
    #             '-f017b14fb8ef/IncomingWebhook/b47f0df154984706812245c006ac3ca5/234c89c3-03e7-4132-92ef-f0c9fb0591d6'
    # section_body = [{
    #     'facts': [
    #         {
    #             "name": "Date",
    #             "value": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #         },
    #         {
    #             "name": "Service",
    #             "value": 'insights'
    #         },
    #         {
    #             "name": "Status",
    #             "value": 'OK'
    #         }
    #     ]
    # }]
    #
    # notification = Notification()
    # notification.msteams_send_msg(channel=to_channel, service='insights', status='200')
