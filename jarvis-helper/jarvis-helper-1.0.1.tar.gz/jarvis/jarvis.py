#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 14/07/2017 11:13
# @Author  : Zhang Lei
# @Site    : 
# @File    : jarvis
# @Software: PyCharm
from ops.args import ArgsHandle
from ops.git import GitHandler
from copy import deepcopy
import time
import datetime
import sys
from ecs import Ecs


def ecs_handle():
    ecs_args = ArgsHandle().get_args()
    ecs_args['cn-north-1-ecr'] = '022524252788.dkr.ecr.cn-north-1.amazonaws.com.cn'
    ecs_args['us-east-1-ecr'] = '747875099153.dkr.ecr.us-east-1.amazonaws.com'

    # sync from git
    git_handler = GitHandler()
    if ecs_args['git_flag']:
        git_handler.git_pull()

    # auto Deploy
    auto_deploy = Ecs(**ecs_args)
    latest_task_def = auto_deploy.generate_task_definition_latest_version()
    latest_task_def = auto_deploy.clean_task_definition_empty_value(task_definition=latest_task_def)
    latest_container_def = deepcopy(latest_task_def['containerDefinitions'][0])
    latest_container_def['taskRoleArn'] = latest_task_def['taskRoleArn'].split('/')[-1]

    # task def family
    task_def_family = auto_deploy.get_task_definition_family()
    if not task_def_family:
        sys.exit("please create ecs service before register new task.")

    service_deployment_config = auto_deploy.get_service_deployment_config()
    # deploy
    remote_task_def = auto_deploy.get_remote_task_definition(task_definition_family=task_def_family)
    remote_task_def = auto_deploy.clean_task_definition_empty_value(task_definition=remote_task_def)
    remote_container_def = deepcopy(remote_task_def['containerDefinitions'][0])
    remote_container_def['taskRoleArn'] = remote_task_def['taskRoleArn'].split('/')[-1]
    # deploy change set
    update_change_set = auto_deploy.get_task_definition_change_set(remote_task_definition=remote_container_def,
                                                                   latest_task_definition=latest_container_def)
    display_msg = "***no environment change in this update***, Re-run with --force or Enter \'Y\' or \'y\' to force continue: \n"
    auto_deploy.no_update_deploy_mode(deploy_change_set=update_change_set, msg=display_msg)

    # deploy msg change set
    deploy_msg = ''
    if len(update_change_set) > 0:
        for index in range(len(update_change_set)):
            deploy_msg += """
                    %s
                    """ % str(update_change_set[index])
    else:
        deploy_msg = 'force update'
    print "Deploy details %s " % deploy_msg

    latest_task_def['family'] = task_def_family
    auto_deploy.register_new_task_definition(**latest_task_def)

    update_cluster_service_info = auto_deploy.update_cluster_service(task_definition_family=task_def_family,
                                                                     service_deployment=service_deployment_config)

    # ecs strategy
    ecs_placementStrategy = '''
        placementConstraints:
            %s
        placementStrategy: 
            %s
        ''' % (update_cluster_service_info['placementConstraints'], update_cluster_service_info['placementStrategy'])
    print "Current Service: %s" % update_cluster_service_info['service'], ecs_placementStrategy

    # commit change to git
    if ecs_args['git_flag']:
        git_handler.git_commit(update_msg=deploy_msg)

    # update_cluster_service_info = {'cluster': 'ecs-s-common-solr-prod2',
    #                                'service': 'asg-ecs-s-bulk-search-prod2-Service-XCZCOJEXW6HB',
    #                                'desiredCount': 2}

    # check update status, retry 10times, interval time is 30s
    retry_time = 1
    retry_times = 15
    while retry_time <= retry_times:
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " updating, please wait ... %s/%s tries" % (
        retry_time, retry_times)
        update_service_status = auto_deploy.check_service_status(service_info=update_cluster_service_info)
        if update_service_status['runningCount'] == update_cluster_service_info['desiredCount'] \
                and update_service_status['status'] == 'ACTIVE' \
                and update_service_status['deployments'] == 1 \
                and 'has reached a steady state' in update_service_status['events_msg']:
            print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " Update finished"
            sys.exit()
        else:
            retry_time += 1
            time.sleep(30)
    sys.exit("update failed, please roll back manually!")

if __name__ == '__main__':
    args = ArgsHandle().get_args()
    if args['tag'] == 'ecs':
        ecs_handle()
