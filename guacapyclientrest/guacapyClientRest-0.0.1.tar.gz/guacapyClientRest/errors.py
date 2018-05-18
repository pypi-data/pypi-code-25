# -*- coding: UTF-8 -*-
import re #正则表达式对错误内容进行替换


class GuacamoleError(Exception):
    '''自定义一个异常类'''
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def ErrorMessageTrans(self,username):
        '''
        处理用户已经存在的异常信息
        :param err:  str形式的错误
        :param username:  用户名称
        :return: <dict>格式的错误信息
                {'expected': None, 'message': 'User xujing2 already exists.', 'type': 'BAD_REQUEST',
                    'translatableMessage': {'variables': None, 'key': 'User xujing2 already exists.'},
                    'statusCode': None}
                <type 'dict'>
        '''
        #替换掉名字前面的 \"
        strinfo = re.compile('\\\\"' + username + '\\\\"')
        err = strinfo.sub(username,self.value)
        #替换字符串中的Null
        strinfo = re.compile('null')
        err = strinfo.sub('None',err)
        errJson = eval(err)
        return errJson

class UserGroupError(Exception):
    def __init__(self,value):
        Exception.__init__(self)
        self.value = value

    def ErrorMessageTrans(self,groupName):
        strinfo = re.compile('\\\\"' + groupName + '\\\\"')
        err = strinfo.sub(groupName,self.value)

        strinfo = re.compile('null')
        err = strinfo.sub('None',err)
        errJson = eval(err)
        return errJson



