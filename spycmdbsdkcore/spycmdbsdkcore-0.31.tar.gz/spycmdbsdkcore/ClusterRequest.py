# coding=utf-8

from spycmdbsdkcore.client import doRequest

class ClusterRequest(object):
    def __init__(self, appid, appkey):
        self.__params = None
        self.appid = appid
        self.appkey = appkey
        self.add_query_param('appid', self.appid)
        self.add_query_param('appkey', self.appkey)

    def add_query_param(self, k, v):
        if self.__params is None:
            self.__params = {}
        self.__params[k] = v

    def set_action_name(self, action_name):
        #self.add_query_param('action_name', action_name)
        self.action_name = action_name

    def set_host_ips(self, ips):
        self.add_query_param('ips', ips)

    def set_PageNumber(self, PageNumber):
        self.add_query_param('PageNumber', PageNumber)

    def set_ClusterId(self, ClusterId):
        self.__ClusterId = ClusterId

    def doClusterRequest(self):
        self.action_name = '/cluster/{0}/'.format(self.action_name)
        return doRequest(self.action_name, self.__params)