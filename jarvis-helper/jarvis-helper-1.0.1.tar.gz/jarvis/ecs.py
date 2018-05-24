#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/03/2018 14:39
# @Author  : Zhang Lei
# @Site    : 
# @File    : ecs
# @Software: PyCharm
import sys
import re
import json
import yaml
import os
from botocore.exceptions import *
from dictdiffer import diff
from ops import timeout
from ops.serviceclient import ServiceClient


class Ecs(object):

    def __init__(self, **kwargs):
        # aws service client
        self.__ecs_client = ServiceClient(**kwargs).get_service_client()
        self.__project = kwargs.get('project')  # s-search-classification-solr
        self.__env = kwargs.get('env')
        self.__region = kwargs.get('region')
        self.__ecr = kwargs.get('%s-ecr' % self.__region)
        self.__force_flag = kwargs.get('force_flag')
        self.__tag = kwargs.get('tag')
        self.__service_name = re.split('-', self.__project)[2:]  # ['classification','solr']
        self.__team = ''.join(re.split('-', self.__project)[1:2])  # 'search'

        if 'details' in kwargs.keys():
            if 'image' in kwargs['details'].keys():
                self.__image_version = kwargs.get('details').get('image')
            else:
                self.__image_version = None

            if 'resource' in kwargs['details'].keys():
                self.__resource = kwargs.get('details').get('resource') + '-'
            else:
                self.__resource = ''

            # default: s-search-classification-solr-prod2, if resource = 'logstash'
            # logstash-s-search-classification-solr-prod2
            self.__pattern = self.__resource + self.__project + '-' + self.__env

            if 'index' in kwargs['details'].keys():
                self.__index_date = kwargs.get('details').get('index')
            else:
                self.__index_date = None

            if 'format' not in kwargs['details'].keys():
                self.__file_format = 'json'
            else:
                self.__file_format = kwargs.get('details').get('format')

            if 'file' in kwargs['details'].keys():
                self.__service_config_dir = kwargs.get('details').get('file')
                # './apps/ecs/search/s-search-ac-solr/cn-north=1/release_'
                self.__service_config_prefix = '%s/%s/%s/%s/%s/' \
                                               % (self.__service_config_dir, self.__team, self.__project,
                                                  self.__env, self.__region)
            else:
                if os.path.dirname(__file__) == '':
                    self.__service_config_dir = '.'
                else:
                    self.__service_config_dir = os.path.dirname(__file__)
                self.__service_config_prefix = '%s/apps/%s/%s/%s/%s/' \
                                               % (self.__service_config_dir, self.__team, self.__project,
                                                  self.__env, self.__region)
        self.__task_definition_file = self.__service_config_prefix + 'task.' + self.__file_format
        self.__service_deployment_file = self.__service_config_prefix + 'deployment.' + self.__file_format

        if not os.path.isfile(self.__service_deployment_file):
            self.__service_deployment_file = '%s/../../%s_deployment.%s' \
                                             % (self.__service_config_prefix, self.__env, self.__file_format)
            if not os.path.isfile(self.__service_deployment_file):
                self.__service_deployment_file = '%s/../../../%s_deployment.%s' \
                                             % (self.__service_config_prefix, self.__env, self.__file_format)
                if not os.path.isfile(self.__service_deployment_file):
                    self.__service_deployment_file = '%s/../../../../%s_deployment.%s' \
                                                 % (self.__service_config_prefix, self.__env, self.__file_format)

    # this function is used to update docker image version and index data if changed
    def generate_task_definition_latest_version(self):
        with open(self.__task_definition_file, 'r') as f:
            if self.__file_format == 'json':
                task_def = json.load(f)
            elif self.__file_format == 'yaml':
                task_def = yaml.load(f)
            else:
                sys.exit("wrong file format! \'json\'|\'yaml\' is available!")

        if self.__index_date is not None:
            task_environment_list = task_def['containerDefinitions'][0]['environment']
            for index in range(len(task_environment_list)):
                # set patten format like : "classification_DATA_DATE"
                data_patten = '_'.join(self.__service_name[:-1]) + '_DATA_DATE'
                # search in environment , if match update index date
                if re.search(data_patten, task_environment_list[index]['name'], re.IGNORECASE):
                    task_def['containerDefinitions'][0]['environment'][index]['value'] = self.__index_date
                    break

        if self.__image_version is not None:
            task_def['containerDefinitions'][0]['image'] = self.__ecr + '/' + self.__team + '/' + self.__image_version
        print "generate new task definition successfully, start to write to file!"
        with open(self.__task_definition_file, 'w') as f:
            if self.__file_format == 'json':
                json.dump(task_def, f, indent=4, sort_keys=True)
            else:
                yaml.dump(task_def, f, indent=4, default_flow_style=False)
        return task_def

    # the function is to get task definition family
    def get_task_definition_family(self):
        try:
            task_result_num = 100
            task_next_token = ''
            while(task_result_num == 100):
                task_kwargs = {
                    'status': 'ACTIVE'
                }
                # task_kwargs['status'] = 'ACTIVE'
                if task_next_token:
                    task_kwargs['nextToken'] = task_next_token
                task_definition_families = self.__ecs_client.list_task_definition_families(**task_kwargs)
                families_list = task_definition_families['families']
                task_next_token = task_definition_families.get('nextToken', None)
                task_result_num = len(families_list)

                for index in range(task_result_num):
                    # search which task definition the role belongs to
                    if re.search(self.__pattern, families_list[index], re.IGNORECASE):
                            def_family = families_list[index]
                            return def_family
        except ParamValidationError, e:
            print "failed get task definition family ", e

    def get_remote_task_definition(self, task_definition_family):
        remote_task_definition = self.__ecs_client.describe_task_definition(
            taskDefinition=task_definition_family
        )['taskDefinition']

        return remote_task_definition

    def clean_task_definition_empty_value(self, task_definition):
        clean_task_definition = task_definition
        for empty_key in clean_task_definition.keys():
            if isinstance(clean_task_definition[empty_key], list):
                if len(clean_task_definition[empty_key]) == 0 and empty_key != 'environment':
                    clean_task_definition.pop(empty_key)
                else:
                    for index in range(len(clean_task_definition[empty_key])):
                        if isinstance(clean_task_definition[empty_key][index], dict):
                            self.clean_task_definition_empty_value(task_definition=clean_task_definition[empty_key][0])
        return clean_task_definition

    def get_task_definition_change_set(self, latest_task_definition, remote_task_definition):
        # change_set = diff(remote_task_definition, latest_task_definition)
        # print list(change_set)
        change_set = []
        remote_environment_dict = {}
        latest_environment_dict = {}
        for key in latest_task_definition.keys():
            if key != 'environment':
                change_set_g = diff(remote_task_definition, latest_task_definition, ignore=set(['environment']))
                change_set = list(change_set_g)
            else:
                for index in range(len(remote_task_definition['environment'])):
                    remote_environment_dict['%s' % remote_task_definition['environment'][index]['name']] = \
                        remote_task_definition['environment'][index]['value']
                # print dict(remote_environment_dict)
                for index in range(len(latest_task_definition['environment'])):
                    latest_environment_dict['%s' % latest_task_definition['environment'][index]['name']] = \
                        latest_task_definition['environment'][index]['value']
                # print dict(latest_environment_dict)

        try:
            for key in latest_environment_dict.keys():
                if key not in remote_environment_dict.keys() or latest_environment_dict[key] != remote_environment_dict[key]:
                    change_set.append(('change', 'environment', key,
                                       ('%s' % remote_environment_dict.get(key, None),
                                        '---->',
                                        '%s' % latest_environment_dict.get(key, None))))
        except Exception, e:
            print e
        return change_set

    def get_service_deployment_config(self):
        with open(self.__service_deployment_file, 'r') as f:
            if self.__file_format == 'json':
                update_service_deployment = json.load(f)
            elif self.__file_format == 'yaml':
                update_service_deployment = yaml.load(f)
            else:
                sys.exit("wrong file format! \'json\'|\'yaml\' is available!")
            for key, value in update_service_deployment.items():
                if value == '':
                    if key == 'clusterName':
                        update_service_deployment['clusterName'] = self.__tag + '-' + self.__team + '-' + self.__env
                    else:
                        sys.exit("%s's value is empty" % key)
        return update_service_deployment

    # this function is to update task definition via loading from task.json
    def register_new_task_definition(self, **kwargs):
        # register new task definition with above json
        self.__ecs_client.register_task_definition(**kwargs)

    @timeout.timeout(10)
    def no_update_deploy_mode(self, deploy_change_set, msg):
        if not isinstance(deploy_change_set, list):
            sys.exit('deploy_flag must be a change set list')
        # exit if no change in task definition
        if not self.__force_flag:
            if len(deploy_change_set) == 0:
                continue_signal = raw_input(msg)
                if continue_signal == 'Y' or continue_signal == 'y':
                    print '*******start updating!*******'
                else:
                    print "Only \'Y\' and \'y\' is available! Please try again! "
                    sys.exit()

    # this function is to apply new task definition with service via loading service.json
    def update_cluster_service(self, task_definition_family, service_deployment):
        update_response = {}
        update_service_info = {}
        update_service_name = ''
        update_cluster_name = self.__tag + '-' + self.__team + '-' + self.__env
        if service_deployment['clusterName'] != update_cluster_name:
            print "You are launching ecs service in cluster %s !\n Usually, you should launch this service in %s " \
                  % (service_deployment['clusterName'], update_cluster_name)
        # assign aws ecs credential
        try:
            service_max_num = 100
            service_next_token = ''
            while(service_max_num == 100):
                service_kwargs = {
                    'cluster': service_deployment['clusterName'],
                    'maxResults': service_max_num
                }
                if service_next_token:
                    service_kwargs['nextToken'] = service_next_token
                service_list = self.__ecs_client.list_services(**service_kwargs)['serviceArns']
                service_max_num = len(service_list)
                service_next_token = self.__ecs_client.list_services(**service_kwargs).get('nextToken', None)

                # find which service should be update via service role
                for index in range(len(service_list)):
                    if re.search(self.__pattern, service_list[index], re.IGNORECASE):
                        update_service_name = service_list[index]
                        break
            if update_service_name == '':
                sys.exit("failed finding update service: %s" % self.__pattern)

        except Exception, e:
            print "failed finding update service ", e

        # update service
        try:
            update_response = self.__ecs_client.update_service(
                cluster=service_deployment['clusterName'],
                service=update_service_name,
                desiredCount=service_deployment['desiredCount'],
                taskDefinition=task_definition_family,
                deploymentConfiguration=service_deployment['deploymentConfiguration'],
                forceNewDeployment=service_deployment.get('forceNewDeployment', False),
                healthCheckGracePeriodSeconds=service_deployment.get('healthCheckGracePeriodSeconds', 60)
            )
        except ClientError:
            update_response = self.__ecs_client.update_service(
                cluster=service_deployment['clusterName'],
                service=update_service_name,
                desiredCount=service_deployment['desiredCount'],
                taskDefinition=task_definition_family,
                deploymentConfiguration=service_deployment['deploymentConfiguration']
            )
        except Exception, e:
            print e
            print "failed update service, please check service deployment configuration! "

        update_service_info['cluster'] = service_deployment['clusterName']
        update_service_info['desiredCount'] = service_deployment['desiredCount']
        update_service_info['service'] = update_service_name
        update_service_info['placementConstraints'] = update_response['service']['placementConstraints']
        update_service_info['placementStrategy'] = update_response['service']['placementStrategy']
        return update_service_info

    def check_service_status(self, service_info):
        update_status = {}
        service_status = self.__ecs_client.describe_services(
            cluster=service_info['cluster'],
            services=[service_info['service'], ]
        )
        update_status['status'] = service_status['services'][0]['status']
        update_status['runningCount'] = service_status['services'][0]['runningCount']
        update_status['deployments'] = len(service_status['services'][0]['deployments'])
        update_status['events_msg'] = service_status['services'][0]['events'][0]['message']
        return update_status
