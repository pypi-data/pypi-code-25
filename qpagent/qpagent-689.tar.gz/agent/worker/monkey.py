# -*- coding: utf-8 -*-
"""
    agent.worker.android_monkey
    ~~~~~~~~~~~~

    This module provide the android monkey.

    :copyright: (c) 2017 by Ma Fei.
"""
import commands
import logging
import os
import re
import time

from agent.api.grand import GrandClient
from agent.api.jira import JiraClient
from agent.api.qualityplatform import QualityPlatform
from agent.util.tools import AppToolKit, FileToolKit
from agent.util.tools import STF
from agent.worker.base import BaseWorker

logger = logging.getLogger(__name__)

app_tool_kit = AppToolKit()
file_tool_kit = FileToolKit()

android_monkey_dir = file_tool_kit.make_worker_dir(os.getcwd() + '/agent/androidMonkey/')

qualityplatform_client = QualityPlatform(os.environ["AGENT_ENV"])
grand_client = GrandClient()
jira_client = JiraClient()


class AndroidMonkey(BaseWorker):
    def __init__(self, data):
        super(AndroidMonkey, self).__init__(data)
        self.device_id = self.data.get('device_id')
        self.device = self.data.get('device')
        self.packtype = self.data.get('packtype')

        self.log_file_dir = os.path.join(android_monkey_dir, str(self.task_id))
        file_tool_kit.make_worker_dir(self.log_file_dir)
        self.android_monkey_log = os.path.join(self.log_file_dir, 'monkey')

    def start_worker(self):
        STF.add_user_device(self.device_id)
        app_tool_kit.unlock(self.device_id)
        app_tool_kit.enable_wifi(self.device_id)
        app_tool_kit.open_status_bar(self.device_id)

        app_tool_kit.uninstall_android_app(self.device_id, 'me.ele')
        app_tool_kit.install_android_app(self.device_id, '/Users/mobile.test/eleme.qa/app/warlock.apk')
        monkey_duration = self.start_monkey(self.device_id)
        mail_content = self.deal_with_log(self.android_monkey_log, monkey_duration)
        if mail_content == '':
            mail_content = 'No crash happened'
            status = 1
        else:
            status = 0
            mail_content = 'http://10.12.38.81/androidmonkey/{}/monkey.txt'.format(str(self.task_id))
            self.upload(self.log_file_dir, '/androidmonkey/{}'.format(str(self.task_id)))
            jira_client.add_jira_issue('UTM', 'Monkey Error Log', mail_content)
        app = {
            "appVersion": "7.38",
            "packageType": 'Release',
            "downloadURL": "http://10.12.38.81/app/warlock.apk"
        }
        qualityplatform_client.add_stability_report(mail_content, status, 'Android',
                                                    self.device,
                                                    app, self.device_id)
        self.complete()
        STF.delete_user_device(self.device_id)
        app_tool_kit.close_status_bar(self.device_id)

    @staticmethod
    def stop_monkey(device_id):
        for i in xrange(10):
            status, output = commands.getstatusoutput('adb -s %s shell ps | grep monkey' % device_id)
            if output == "error: device not found":
                logger.debug("Please check device")
            elif output == "":
                logger.info("no monkey running in %s" % device_id)
                break
            else:
                output = re.search('shell     [0-9]+', output).group()
                pid = re.search('[0-9]+', output).group()
                logger.info("kill the monkey process: %s in %s" % (pid, device_id))
                commands.getstatusoutput("adb -s %s shell kill %s" % (device_id, pid))
            time.sleep(2)

    def start_monkey(self, device_id):
        logger.info("start monkey with {}".format(device_id))
        monkey_start_time = time.time()
        cmd_monkey = "adb -s " + self.device_id + " shell monkey -p me.ele" \
                     + " --throttle 300 --pct-touch 30 --pct-motion 20 --pct-appswitch 50 " \
                     + "--ignore-crashes --ignore-timeouts --ignore-security-exceptions --monitor-native-crashes" \
                     + " -v -v 20000 >" + self.android_monkey_log + ".txt"
        logger.info("Monkey cmd: {}".format(cmd_monkey))
        commands.getstatusoutput(cmd_monkey)
        logger.info("monkey end with {}".format(device_id))
        monkey_end_time = time.time()
        monkey_duration = round((monkey_end_time - monkey_start_time) / 3600, 2)
        return str(monkey_duration)

    @staticmethod
    def deal_with_log(log_file_name_with_location, monkey_duration):
        # analyze with log:
        logger.info("deal_with_log")
        f_full_log = open(log_file_name_with_location + '.txt', 'r')
        full_log = f_full_log.readlines()
        f_full_log.close()
        full_log_lines_number = len(full_log)
        anr = 'NOT RESPONDING'
        crash = 'Crash'
        exception = 'Exception'
        mail_content = ''
        for i in xrange(full_log_lines_number):
            if (exception in full_log[i]) | (anr in full_log[i]) | (crash in full_log[i]):
                f_crash_log = open(log_file_name_with_location + '.txt', 'r')
                f_crash_log.close()
                for j in range(i, full_log_lines_number):
                    mail_content = mail_content + full_log[j] + '\r'
                break
        if mail_content == "":
            return mail_content
        tmp = log_file_name_with_location.split('/')
        log_file_name = tmp[-1]
        mail_content = log_file_name + '_' + monkey_duration + "hour" + '\r\r' + mail_content
        return mail_content

    def clear(self):
        pass
