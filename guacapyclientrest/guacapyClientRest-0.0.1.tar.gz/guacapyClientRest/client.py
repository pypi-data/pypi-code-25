#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from simplejson.scanner import JSONDecodeError
import logging
import re
import requests


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from errors import (GuacamoleError)


class Guacamole():
    def __init__(self, hostname, username, password, default_datasource=None,
                 verify=True):
        self.REST_API = 'http://{}/guacamole'.format(hostname)
        self.username = username
        self.password = password
        self.verify = verify
        auth = self.__authenticate()
        assert 'authToken' in auth, 'Failed to retrieve auth token'
        assert 'dataSource' in auth, 'Failed to retrieve primaray data source'
        assert 'availableDataSources' in auth, 'Failed to retrieve data sources'
        self.datasources = auth['availableDataSources']
        if default_datasource:
            assert default_datasource in self.datasources, \
                'Datasource {} does not exist. Possible values: {}'.format(
                    default_datasource, self.datasources
                )
            self.primary_datasource = default_datasource
        else:
            self.primary_datasource = auth['dataSource']
        self.token = auth['authToken']

    def __authenticate(self):
        r = requests.post(
            url=self.REST_API + "/api/tokens",
            data={'username': self.username, 'password': self.password},
            verify=self.verify,
            allow_redirects=True
        )

        r.raise_for_status()
        return r.json()

    def __auth_request(self, method, url, payload=None, url_params=None,
                       json_response=True):
        params = [('token', self.token)]
        if url_params:
            params += url_params
        logger.debug(
            '{method} {url} - Params: {params}- Payload: {payload}'.format(
                method=method, url=url, params=params, payload=payload
            )
        )

        r = requests.request(
            method=method,
            url=url,
            params=params,
            json=payload,
            verify=self.verify,
            allow_redirects=True
        )
        if not r.ok:

            logger.error(r.text)
            raise GuacamoleError(r.content)

        r.raise_for_status()
        if json_response:
            try:
                return r.json()
            except JSONDecodeError:
                logger.error('Could not decode JSON response')
                return r
        else:
            return r

    def user_token_authenticate(self):
        '''
        用户token验证和获取
        :return:
        '''
        r = requests.post(
            url=self.REST_API + "/api/tokens",
            data={'username': self.username, 'password': self.password},
            verify=self.verify,
            allow_redirects=True
        )

        # r.raise_for_status()
        # return r.json()

        if not r.ok:

            logger.error(r.text)
            raise GuacamoleError(r.content)

        r.raise_for_status()
        return r.json()

    def get_connections(self, datasource=None):
        '''
        获取所有的桌面连接
        get all existed connections
        :param datasource: default mysql
        :return:
        '''
        if not datasource:
            datasource=self.primary_datasource
        params = [
            ('permission', 'UPDATE'),
            ('permission', 'DELETE'),
        ]
        return self.__auth_request(
            method='GET',
            # url='{}/data/{}/connectionGroups/ROOT/tree'.format(
            url = '{}/api/session/data/{}/connectionGroups/ROOT/tree'.format(
                self.REST_API, datasource
            ),
            url_params=params
        )

    def get_active_connections(self, datasource=None):
        '''
        get all active connections
        获取所有正在连接的连接
        :param datasource: default mysql
        :return: <dict>
        '''
        if not datasource:
            datasource=self.primary_datasource
        return self.__auth_request(
            method='GET',
            url='{}/api/session/data/{}/activeConnections'.format(
                self.REST_API, datasource
            )
        )

    def get_connection(self, connection_id, datasource=None):
        '''
        获取指定connection的信息
        :param connection_id: the connection_id in mysql database table `guacamole_connection`
        :param datasource: default mysql
        :return: <dict>
        '''
        if not datasource:
            datasource=self.primary_datasource
        return self.__auth_request(
            method='GET',
            url='{}/api/session/data/{}/connections/{}'.format(
                self.REST_API, datasource, connection_id
            )
        )

    def get_connection_parameters(self, connection_id, datasource=None):
        '''
        获取指定connection的所有配置参数信息
        get all info of an appointed connection
        :param connection_id: the connection_id in mysql database table `guacamole_connection`
        :param datasource: default mysql
        :return: <dict>
        '''
        if not datasource:
            datasource=self.primary_datasource
        return self.__auth_request(
            method='GET',
            url='{}/api/session/data/{}/connections/{}/parameters'.format(
                self.REST_API, datasource, connection_id
            )
        )

    def get_connection_full(self, connection_id, datasource=None):
        '''
        获取指定连接的所有信息
        将get_connection信息和get_connection_parametras信息合并在一起
        :param connection_id: the connection_id in mysql database table `guacamole_connection`
        :param datasource: default mysql
        :return:
        '''
        c = self.get_connection(connection_id, datasource)
        c['parameters'] = self.get_connection_parameters(
            connection_id, datasource
        )
        return c

    def __get_connection_by_name(self, cons, name, regex=False):
        # FIXME This need refactoring (DRY)
        if 'childConnections' not in cons:
            if 'childConnectionGroups' in cons:
                for c in cons['childConnectionGroups']:
                    res = self.__get_connection_by_name(c, name, regex)
                    if res:
                        return res
        else:
            children = cons['childConnections']
            if regex:
                res = [x for x in children if re.match(name, x['name'])]
            else:
                res = [x for x in children if x['name'] == name]
            if not res:
                if 'childConnectionGroups' in cons:
                    for c in cons['childConnectionGroups']:
                        res = self.__get_connection_by_name(c, name, regex)
                        if res:
                            return res
            else:
                return res[0]

    def get_connection_by_name(self, name, regex=False, datasource=None):
        '''
        Get a connection group by its name
        获取一个连接根据它的名字
        :param name: the connection_name in mysql database table `guacamole_connection`
        :param regex:
        :param datasource: default mysql
        :return:
        '''
        cons = self.get_connections(datasource)
        res = self.__get_connection_by_name(cons, name, regex)
        if not res:
            logger.error(
                'Could not find connection named {}'.format(name)
            )
        return res


    def add_connection(self, payload, datasource=None):
        '''
         Add a new connection 添加一个连接
        :param payload:
        Example payload:
        {"name":"iaas-067-mgt01 (Admin)",
        "parentIdentifier":"4",
        "protocol":"rdp",
        "attributes":{"max-connections":"","max-connections-per-user":""},
        "activeConnections":0,
        "parameters":{
            "port":"3389",
            "enable-menu-animations":"true",
            "enable-desktop-composition":"true",
            "hostname":"iaas-067-mgt01.vcloud",
            "color-depth":"32",
            "enable-font-smoothing":"true",
            "ignore-cert":"true",
            "enable-drive":"true",
            "enable-full-window-drag":"true",
            "security":"any",
            "password":"XXX",
            "enable-wallpaper":"true",
            "create-drive-path":"true",
            "enable-theming":"true",
            "username":"Administrator",
            "console":"true",
            "disable-audio":"true",
            "domain":"iaas-067-mgt01.vcloud",
            "drive-path":"/var/tmp",
            "disable-auth":"",
            "server-layout":"",
            "width":"",
            "height":"",
            "dpi":"",
            "console-audio":"",
            "enable-printing":"",
            "preconnection-id":"",
            "enable-sftp":"",
            "sftp-port":""}}
        :param datasource: default mysql
        :return:<dict>
        {
         "parentIdentifier": "ROOT",
         "protocol": "rdp",
         "name": "iaas-067",
         "parameters": {
          "domain": "iaas-067-mgt01.vcloud",
          "enable-theming": "true",
          "height": "",
          "drive-path": "/var/tmp",
          "disable-auth": "",
          "enable-full-window-drag": "true",
          "port": "3389",
          "console": "true",
          "enable-wallpaper": "true",
          "hostname": "192.168.20.137",
          "width": "",
          "enable-font-smoothing": "true",
          "sftp-port": "",
          "username": "root",
          "enable-sftp": "",
          "enable-drive": "true",
          "preconnection-id": "",
          "server-layout": "",
          "enable-printing": "",
          "password": "qwe123!@#",
          "console-audio": "",
          "ignore-cert": "true",
          "disable-audio": "true",
          "enable-desktop-composition": "true",
          "create-drive-path": "true",
          "color-depth": "32",
          "security": "any",
          "dpi": "",
          "enable-menu-animations": "true"
         },
         "activeConnections": 0,
         "attributes": {
          "max-connections-per-user": "2",
          "max-connections": "2"
         },
         "identifier": "15"
        }

        '''
        if not datasource:
            datasource=self.primary_datasource
        return self.__auth_request(
            method='POST',
            url='{}/api/session/data/{}/connections'.format(
                self.REST_API,
                datasource
            ),
            payload=payload,
        )

    def edit_connection(self, connection_id, payload, datasource=None):
        '''
        Edit an existing connection
        修改一个指定的存在的连接
        :param connection_id:指定的连接id
        :param payload: Example payload:
        {"name":"test",
        "identifier":"7",
        "parentIdentifier":"ROOT",
        "protocol":"rdp",
        "attributes":{"max-connections":"","max-connections-per-user":""},
        "activeConnections":0,
        "parameters":{
            "disable-audio":"true",
            "server-layout":"fr-fr-azerty",
            "domain":"dt",
            "hostname":"127.0.0.1",
            "enable-font-smoothing":"true",
            "security":"rdp",
            "port":"3389",
            "disable-auth":"",
            "ignore-cert":"",
            "console":"",
            "width":"",
            "height":"",
            "dpi":"",
            "color-depth":"",
            "console-audio":"",
            "enable-printing":"",
            "enable-drive":"",
            "create-drive-path":"",
            "enable-wallpaper":"",
            "enable-theming":"",
            "enable-full-window-drag":"",
            "enable-desktop-composition":"",
            "enable-menu-animations":"",
            "preconnection-id":"",
            "enable-sftp":"",
            "sftp-port":""}}
        :param datasource:default mysql
        :return:<Response [204]>
        '''
        if not datasource:
            datasource=self.primary_datasource
        return self.__auth_request(
            method='PUT',
            url='{}/api/session/data/{}/connections/{}'.format(
                self.REST_API,
                datasource,
                connection_id
            ),
            payload=payload,
        )

    def delete_connection(self, connection_id, datasource=None):
        '''
        delete an appointed connection 删除一个指定id的连接
        :param connection_id:
        :param datasource: default mysql
        :return: <Response [204]>
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='DELETE',
            url='{}/api/session/data/{}/connections/{}'.format(
                self.REST_API,
                datasource,
                connection_id
            ),
        )

    def get_connection_history(self, connection_id,datasource=None):
        '''
        获取连接的历史信息
        :param connection_id:
        :param datasource: default mysql
        :return: <list>
        [
         {
          "username": "guacadmin",
          "startDate": 1514451720000,
          "endDate": 1514451720000,
          "remoteHost": null,
          "connectionName": "aaaa",
          "active": false,
          "sharingProfileName": null,
          "connectionIdentifier": "10",
          "sharingProfileIdentifier": null
         },
         {
          "username": "seu_test",
          "startDate": 1514449747000,
          "endDate": 1514449747000,
          "remoteHost": null,
          "connectionName": "aaaa",
          "active": false,
          "sharingProfileName": null,
          "connectionIdentifier": "10",
          "sharingProfileIdentifier": null
         }
        ]
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='GET',
            url='{}/api/session/data/{}/connections/{}/history'.format(
                self.REST_API,
                datasource,
                connection_id
            ),
        )



    def __get_connection_group_by_name(self, cons, name, regex=False):
        if 'childConnectionGroups' in cons:
            children = cons['childConnectionGroups']
            if regex:
                res = [x for x in children if re.match(name, x['name'])]
            else:
                res = [x for x in children if x['name'] == name]
            if res:
                return res[0]
            for c in cons['childConnectionGroups']:
                res = self.__get_connection_group_by_name(c, name, regex)
                if res:
                    return res

    def get_connection_group_by_name(self, name, regex=False, datasource=None):
        '''
        Get a connection group by its name
        根据名字获取connectionGroup信息
        :param name:
        :param regex:
        :param datasource:
        :return:
        '''
        if not datasource:
            datasource = self.primary_datasource
        cons = self.get_connections(datasource)
        return self.__get_connection_group_by_name(cons, name, regex)

    def add_connection_group(self, payload, datasource=None):
        '''
        Create a new connection group
        创建一个新的ConnectionGroup
        :param payload: 
        :param datasource: Example payload:
        {"parentIdentifier":"ROOT",
        "name":"iaas-099 (Test)",
        "type":"ORGANIZATIONAL",
        "attributes":{"max-connections":"","max-connections-per-user":""}}
        :return: {u'parentIdentifier': u'ROOT', u'name': u'test', u'activeConnections': 0, u'attributes': {u'max-connections-per-user': u'4',
              u'max-connections': u'4'}, u'identifier': u'1', u'type': u'ORGANIZATIONAL'}
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='POST',
            url='{}/api/session/data/{}/connectionGroups'.format(
                self.REST_API,
                datasource
            ),
            payload=payload
        )

    def edit_connection_group(self, connection_group_id, payload, datasource=None):
        '''
        Edit an exiting connection group
        编辑修改一个已经存在的ConnectionGroup信息
        :param connection_group_id: id is the connectionGroup_id in table `guacamole_connectionGroup`
        :param payload:
        Example payload:
        {"parentIdentifier":"ROOT",
        "name":"iaas-099 (Test)",
        "type":"ORGANIZATIONAL",
        "attributes":{"max-connections":"","max-connections-per-user":""}}
        :param datasource: default mysql
        :return:
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='PUT',
            url='{}/api/session/data/{}/connectionGroups/{}'.format(
                self.REST_API,
                datasource,
                connection_group_id
            ),
            payload=payload
        )

    def delete_connection_group(self, connection_group_id, datasource=None):
        '''
        delete connection group删除一个connectionGroup
        :param connection_group_id: id is the connectionGroup_id in table `guacamole_connectionGroup`
        :param datasource: default mysql
        :return: <204>
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='DELETE',
            url='{}/api/session/data/{}/connectionGroups/{}'.format(
                self.REST_API,
                datasource,
                connection_group_id
            )
        )


    def get_all_users_info(self, datasource=None):
        '''
        获取所有用户的基本信息
        get all users' basic info
        :param datasource:default mysql
        :return:<dict>
        "seu_test": {
              "username": "seu_test",
              "attributes": {
               "disabled": null,
               "guac-full-name": null,
               "valid-from": null,
               "access-window-end": null,
               "access-window-start": null,
               "guac-organizational-role": null,
               "valid-until": null,
               "guac-organization": null,
               "timezone": null,
               "guac-email-address": null,
               "expired": null
          }
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='GET',
            url='{}/api/session/data/{}/users'.format(
                self.REST_API,
                datasource,
            )
        )

    def get_user_info(self, username, datasource=None):
        '''
        获得指定的用户的信息
        get appointed user's info
        :param username:string
        :param datasource:default mysql
        :return:<dict> or 404
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='GET',
            url='{}/api/session/data/{}/users/{}'.format(
                self.REST_API,
                datasource,
                username
            )
        )

    def add_user(self, payload, datasource=None):
        '''
        添加一个用户，默认user_permission仅有READ
        Add/enable a user
        :param payload:
         Example payload:
        {"username":"test",
         "password":"testpwd",  #mysql会自动hash加密
         "attributes":{
                "disabled":"",
                "expired":"",
                "access-window-start":"",
                "access-window-end":"",
                "valid-from":"",
                "valid-until":"",
                "timezone":None}}
        :param datasource:default mysql
        :return:<dict>
        {
         "username": "test",
         "attributes": {
          "valid-from": "",
          "access-window-end": "",
          "access-window-start": "",
          "disabled": "",
          "valid-until": "",
          "timezone": null,
          "expired": ""
         },
         "password": "testpwd"
        }
        '''
        if not datasource:
            datasource=self.primary_datasource
        return self.__auth_request(
            method='POST',
            url='{}/api/session/data/{}/users'.format(
                self.REST_API,
                datasource
            ),
            payload=payload
        )



    def delete_user(self, username, datasource=None):
        '''
        删除一个指定的用户
        delete appointed user
        :param username:
        :param datasource:
        :return:
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='DELETE',
            url='{}/api/session/data/{}/users/{}'.format(
                self.REST_API,
                datasource,
                username
            ),
        )

    def get_user_permissions(self, username, datasource=None):
        '''
        获取指定用户的所有权限信息
        get appointed user's permissions
        :param username:
        :param datasource:
        :return:<dict>
        {
         "userPermissions": {
          "seu_test": [
           "READ"
          ]
         },
         "sharingProfilePermissions": {},
         "systemPermissions": [],
         "connectionGroupPermissions": {
          "1": [
           "READ"
          ]
         },
         "activeConnectionPermissions": {},
         "connectionPermissions": {}
        }
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='GET',
            url='{}/api/session/data/{}/users/{}/permissions'.format(
                self.REST_API,
                datasource,
                username
            )
        )


    def grant_user_system_permission(self, username, payload, datasource=None):
        '''
        guacamole用户修改指定用户系统权限
        :param username:string
        :param payload: Example payload:
                [{	"op":"add/remove",
            "path":"/systemPermissions",
            "value":"ADMINISTER" #可以取得值包括:
            [CREATE_CONNECTION,CREATE_SHARING_PROFILE,CREATE_USER,ADMINISTER]
        }]
        :param datasource:default mysql
        :return: <Response [204]>
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='PATCH',
            url='{}/api/session/data/{}/users/{}/permissions'.format(
                self.REST_API,
                datasource,
                username
            ),
            payload=payload,
            json_response=False
        )

    def grant_user_user_permission(self,username,payload,datasource=None):
        '''
        guacamole用户修改指定用户的用户权限  感觉不怎么用系列
        :param username: string
        :param payload: Example payload:
                [{	"op":"add/remove",
            "path":"/userPermissions/{user_id}", #user_id
            "value":"ADMINISTER" #可以取得值包括:
            [READ,UPDATE,DELETE,ADMINISTER]
        }]
        :param datasource: default mysql
        :return: <Response [204]>
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='PATCH',
            url='{}/api/session/data/{}/users/{}/permissions'.format(
                    self.REST_API, datasource, username
                ),
            payload = payload
        )

    def grant_user_connection_permission(self, username, payload, datasource=None):
        '''
        guacamole修改指定用户与连接之间的权限
        :param username:string
        :param payload: Example payload:
                [{	"op":"add/remove",
            "path":"/connectionPermissions/{connection_id}", #这里connection_id需要通过函数get_connection("id")获取
            "value":"ADMINISTER" #可以取得值包括:
            [READ,UPDATE,DELETE,ADMINISTER]
        }]
        :param datasource:default mysql
        :return:<Response [204]>
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='PATCH',
            url='{}/api/session/data/{}/users/{}/permissions'.format(
                self.REST_API,
                datasource,
                username
            ),
            payload=payload,
            json_response=False
        )


    def grant_user_connection_groups_permission(self, username, payload, datasource=None):
        '''
        修改指定用户connectionGroups权限
        :param username: string
        :param payload: Example payload:
                [{	"op":"add/remove",
            "path":"/connectionGroupPermissions/{connectionGroups_id}",
            "value":"ADMINISTER" #可以取得值包括:
            [READ,UPDATE,DELETE,ADMINISTER]
        }]
        :param datasource: default mysql
        :return: [204]
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='PATCH',
            url='{}/api/session/data/{}/users/{}/permissions'.format(
                self.REST_API,
                datasource,
                username
            ),
            payload=payload,
            json_response=False
        )

    def grant_user_sharingProfileConnection_permission(self, username, payload, datasource=None):
        '''
        修改指定用户sharingProfilePermission权限
        :param username: string
        :param payload: Example payload:
                [{	"op":"add/remove",
            "path":"/sharingProfilePermissions/{share_connection_id}",
            "value":"ADMINISTER" #可以取得值包括:
            [READ,UPDATE,DELETE,ADMINISTER]
        }]
        :param datasource: default mysql
        :return: [204]
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='PATCH',
            url='{}/api/session/data/{}/users/{}/permissions'.format(
                self.REST_API,
                datasource,
                username
            ),
            payload=payload,
            json_response=False
        )


    def grant_user_activeConnection_permission(self, username, payload, datasource=None):
        '''
        修改指定用户activeConnectionPermission权限
        :param username: string
        :param payload: Example payload:
                [{	"op":"add/remove",
            "path":"/activeConnectionPermissions/{connection_id}",
            "value":"ADMINISTER" #可以取得值包括:
            [READ,UPDATE,DELETE,ADMINISTER]
        }]
        :param datasource: default mysql
        :return: [204]
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='PATCH',
            url='{}/api/session/data/{}/users/{}/permissions'.format(
                self.REST_API,
                datasource,
                username
            ),
            payload=payload,
            json_response=False
        )


    def get_all_sharingProfiles(self):
        '''
        获取所有连接分享的信息
        http://192.168.20.137:8080/guacamole/api/session/data/mysql/sharingProfiles?token=8DECE3D15496DAC68FAF542BEEBFC327446EFA39EFBBC85FB10D415B4E73F301
        对应  guacamole_sharing_Profile
        :param datasource: default mysql
        :return: <dict>
        '''
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method='GET',
            url='{}/api/session/data/{}/sharingProfiles'.format(
                self.REST_API,
                datasource,
                username
            ),
            payload=payload,
            json_response=False
        )

    def add_sharingProfiles(self, payload, datasource=None):
        '''
        将已有的连接添加桌面共享
        :param ConnectionId: 需要被共享的连接ID
        :param shareName:  共享连接命名
        :return: <dict>
        '''

        if not datasource:
            datasource=self.primary_datasource
        return self.__auth_request(
            method='POST',
            url='{}/api/session/data/{}/sharingProfiles'.format(
                self.REST_API,
                datasource
            ),
            payload=payload
        )



    def del_sharingProfiles(self, sharing_profile_id, datasource=None):
        '''
        将已有的共享桌面删除，根据ID
        :param sharing_profile_id: 需要被删除共享ID
        :return: <204>
        '''

        if not datasource:
            datasource=self.primary_datasource
        return self.__auth_request(
            method='DELETE',
            url='{}/api/session/data/{}/sharingProfiles/{}'.format(
                self.REST_API,
                datasource,
                sharing_profile_id
            ),
        )
