"""
#*===================================================================
#*
#* Licensed Materials - Property of IBM
#* IBM Cost And Asset Management
#* Copyright IBM Corporation 2017. All Rights Reserved.
#*
#*===================================================================
"""

import json
import traceback

from path import Path
import pika
import threading
from vmware.extract.cost.client import CostClient
from vmware.extract.assets.client import Client as AssetClient
from vmware.extract.utilization.client import Client as UtilizationClient
from log import configure_logging
from vmware.extract import utils
from os import getenv
from vmware.extract.strings import VMware_strings
import requests
import glob

provider = 'vmware'
run_by = 'pika' #decide on this basis either run by pika or CLI



class Client:

    def __init__(self, workdir):
        self._workdir = workdir

    def callassetandutilization(self, asset_tempdir, utilization_tempdir, ch, properties,
                             billingaccount, assetaccount, period):
        assetobj = AssetClient(Path.getcwd(), asset_tempdir, ch, properties, envextdir,run_by)
        utilizationobj = UtilizationClient(Path.getcwd(), utilization_tempdir, ch, properties, envextdir,run_by)

        assetfile = assetobj.extract_assets_files(billingaccount, assetaccount, period)
        logger.info('asset file %s', assetfile)
        utilizationfile = utilizationobj.extract_utilization_files_vSphere_60(billingaccount, assetaccount, period)
        
        if not assetfile and not utilizationfile:
            body = ''
            if not assetfile:
                body = utils.reply_body('asset', billingaccount, assetaccount['asset_account_number'], VMware_strings.STATUS_GPD_FAILED, "",
                                        VMware_strings.RESPONSE_CODE_INTERNAL_ERROR,
                                        VMware_strings.RESPONSE_FAIL_GPD_CREATE, assetfile)
            if not utilizationfile:
                body = utils.reply_body('utilization', billingaccount, assetaccount['asset_account_number'], VMware_strings.STATUS_GPD_FAILED, "",
                                        VMware_strings.RESPONSE_CODE_INTERNAL_ERROR,
                                        VMware_strings.RESPONSE_FAIL_GPD_CREATE, utilizationfile)
            self.publish_progress(body, ch, properties)
        else:  # on success, send two messages, failure only one
            body = utils.reply_body('asset', billingaccount, assetaccount['asset_account_number'], VMware_strings.STATUS_GPD_CREATED, "",
                                    requests.codes.ok,
                                    VMware_strings.RESPONSE_SUCCESS, assetfile)
            self.publish_progress(body, ch, properties)
            body = utils.reply_body('utilization', billingaccount, assetaccount['asset_account_number'], VMware_strings.STATUS_GPD_CREATED, "",
                                    requests.codes.ok,
                                    VMware_strings.RESPONSE_SUCCESS, utilizationfile)
            self.publish_progress(body, ch, properties)

    def callback(self, ch, method, properties, body):
        tempdir = utils._tempdir()
        message = json.loads(body)
        # In below function we will decide which version's, what accounts to extract
        pdict = utils.process_message(message)  # returns a dictionary of required fields
        default_period = pdict['months']
        cost_threads = {}
        for i,billing_account in enumerate(pdict['accounts']):
            billing_account_number = billing_account['billing_account_number']
            creds = {'vserver':billing_account['vserver'],
                     'username':billing_account['username'],
                     'password':billing_account['password']}
            period = billing_account['months']
            if not period:
                period = default_period
            cost_tempdir_name = 'invoices'
            cost_tempsubdir_name = billing_account_number
            cost_tempdir = tempdir / cost_tempdir_name / cost_tempsubdir_name # create invoices directory under common temp dir
            cost_tempdir.makedirs_p()
            cost = CostClient(Path.getcwd(), cost_tempdir, ch, properties, envextdir,run_by)

            cost_thread = threading.Thread(target=cost.extract_cost_files, args=(billing_account_number, creds, period))
            cost_thread.start()
            cost_threads[billing_account_number] = cost_thread

            asset_utilization_threads = {}  # key = asset_account_number : value = threadname , this is for logging and join
            for i1, asset_account in enumerate(billing_account['asset_accounts']):
                acct = billing_account['billing_account_number']
                asset_tempsubdir = acct
                asset_tempdir = tempdir / 'assets' / asset_tempsubdir  # create asset directory under common temp dir
                asset_tempdir.makedirs_p()
                utilization_tempdir = tempdir / 'utilization' / asset_tempsubdir  # create asset directory under common temp dir
                utilization_tempdir.makedirs_p()
                asset_utilz_channel = utils.create_connection()
                assetutilthread = threading.Thread(target=self.callassetandutilization,
                                                name=asset_account['asset_account_number'],
                                                args=(asset_tempdir, utilization_tempdir, asset_utilz_channel, properties,
                                                    billing_account, asset_account, period))
                assetutilthread.start()
                asset_utilization_threads[asset_account['asset_account_number']] = assetutilthread

    def publish_progress(self, message,channel, properties):
        logger.debug('message to publish : %s', message)
        try:
            self.publish_message(message,channel,properties)
        except: # on connection closed reconnect and publish the message again
            logger.info('Got exception when trying to publish message, reconnecting')
            channel = utils.create_connection()
            self.publish_message(message,channel,properties)

    def publish_message(self, message, channel, properties):
        channel.basic_publish(exchange='', routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),body=str(message))


if __name__ == '__main__':
    try:
        start_process_time = utils.now('%Y%m%d%H%M%S')
        logger = configure_logging('vmware.extract', start_process_time)
        logger.info('~~~~~~~~~~~~~~~~~~~~~~~~start of messaging~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        _config = utils.load()
        broker_config = _config['vmware']['broker']
        # check if environment variable EXTRACTDIR is set, else we exit
        envextdir = getenv('EXTRACTDIR')
        if envextdir is None:
            excmsg = 'environment variable  EXTRACTDIR is none'
            raise EnvironmentError(excmsg)
        if not Path(envextdir).exists():
            excmsg = 'extract directory [ ' + envextdir + ' ] does not exist'
            raise EnvironmentError(excmsg)
        queue = broker_config['queue'] #TODO earlier we decided its by convention and hence no need to get from env. But need to confirm.
        channel = utils.create_connection()
        _work_dir = Path.getcwd()
        myclient = Client(_work_dir)

        # start consuming (blocks)
        # This is a temporary fix to stop pika from crashing everytime a connection fails
        # This will be removed once we move to Kombu
        while True:
            try:
                channel.basic_consume(myclient.callback,
                                      queue=queue,
                                      no_ack=True)
                channel.start_consuming()
            except Exception as e:  # if any connection closed error reconnect and continue consuming messages
                logger.error(traceback.format_exc())
                channel = utils.create_connection()
    except Exception as e:
        logger.error(traceback.format_exc())
