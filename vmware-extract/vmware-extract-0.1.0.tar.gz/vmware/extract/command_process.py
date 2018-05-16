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
import click


# this file will used for running the extractor from CLI

provider = 'vmware'
run_by = 'cmd' #decide on this basis either run by pika or CLI
envextdir=''

class Client:

    def __init__(self, workdir,logger):
        self._workdir = workdir
        self.logger =logger

    def callassetandutilization(self, asset_tempdir, utilization_tempdir, ch, properties,
                                billingaccount, assetaccount, period):
        assetobj = AssetClient(Path.getcwd(), asset_tempdir, ch, properties, envextdir,run_by)
        utilizationobj = UtilizationClient(Path.getcwd(), utilization_tempdir, ch, properties, envextdir,run_by)
        assetfile = assetobj.extract_assets_files(billingaccount, assetaccount, period)
        self.logger.info('asset file %s', assetfile)
        utilizationfile = utilizationobj.extract_utilization_files_vSphere_60(billingaccount, assetaccount, period)

        if not assetfile and not utilizationfile:
            body = ''
            if not assetfile:
                body = utils.reply_body('asset', billingaccount, assetaccount['asset_account_number'],
                                        VMware_strings.STATUS_GPD_FAILED, "",
                                        VMware_strings.RESPONSE_CODE_INTERNAL_ERROR,
                                        VMware_strings.RESPONSE_FAIL_GPD_CREATE, assetfile)
            if not utilizationfile:
                body = utils.reply_body('utilization', billingaccount, assetaccount['asset_account_number'],
                                        VMware_strings.STATUS_GPD_FAILED, "",
                                        VMware_strings.RESPONSE_CODE_INTERNAL_ERROR,
                                        VMware_strings.RESPONSE_FAIL_GPD_CREATE, utilizationfile)
            self.publish_progress(body, ch, properties)
        else:  # on success, send two messages, failure only one
            body = utils.reply_body('asset', billingaccount, assetaccount['asset_account_number'],
                                    VMware_strings.STATUS_GPD_CREATED, "",
                                    requests.codes.ok,
                                    VMware_strings.RESPONSE_SUCCESS, assetfile)
            self.publish_progress(body, ch, properties)
            body = utils.reply_body('utilization', billingaccount, assetaccount['asset_account_number'],
                                    VMware_strings.STATUS_GPD_CREATED, "",
                                    requests.codes.ok,
                                    VMware_strings.RESPONSE_SUCCESS, utilizationfile)
            self.publish_progress(body, ch, properties)

    def callback(self, body,ch=None, method=None, properties=None):
        tempdir = utils._tempdir()
        message = json.loads(body)
        # In below function we will decide which version's, what accounts to extract
        pdict = utils.process_message(message)  # returns a dictionary of required fields
        default_period = pdict['months']
        cost_threads = {}
        for i, billing_account in enumerate(pdict['accounts']):
            billing_account_number = billing_account['billing_account_number']
            creds = {'vserver': billing_account['vserver'],
                     'username': billing_account['username'],
                     'password': billing_account['password']}
            period = billing_account['months']
            if not period:
                period = default_period
            cost_tempdir_name = 'invoices'
            cost_tempsubdir_name = billing_account_number
            cost_tempdir = tempdir / cost_tempdir_name / cost_tempsubdir_name  # create invoices directory under common temp dir
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
                asset_utilz_channel=''
                if run_by != 'cmd':
                    asset_utilz_channel = utils.create_connection()
                assetutilthread = threading.Thread(target=self.callassetandutilization,
                                                   name=asset_account['asset_account_number'],
                                                   args=(
                                                   asset_tempdir, utilization_tempdir, asset_utilz_channel, properties,
                                                   billing_account, asset_account, period,))
                assetutilthread.start()
                asset_utilization_threads[asset_account['asset_account_number']] = assetutilthread

    def publish_progress(self, message, channel, properties):
        self.logger.debug('message to publish : %s', message)
        if run_by == 'cmd':
            self.logger.info(message)
        else:
            try:
                self.publish_message(message, channel, properties)
            except:  # on connection closed reconnect and publish the message again
                self.logger.info('Got exception when trying to publish message, reconnecting')
                channel = utils.create_connection()
                self.publish_message(message, channel, properties)

    def publish_message(self, message, channel, properties):
        channel.basic_publish(exchange='', routing_key=properties.reply_to,
                              properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                              body=str(message))


def _create_json_from_command(*args,**kwargs):
    body={
    "months": "",
    "accounts": [
        {
            "months": 1,
            "billing_account_number": "",
            "credentials": {
                "vserver": "",
                "username": "",
                "password": "",
                "tenant": ""
            },
            "asset_accounts": [
                {
                    "asset_account_number": "",
                    "credentials": {}
                }
            ]
        }
    ]
}
    vcenterhost=kwargs.get("vcenterhost",None)
    user=kwargs.get('user',None)
    password=kwargs.get("password",None)
    vrahost=kwargs.get('vrahost',None)
    tenant=kwargs.get('tenant',None)
    extdir=kwargs.get('extdir',None)
    billingaccount=kwargs.get('billingaccount',None)
    assets_accounts=kwargs.get('assetaccounts',None)
    if not vcenterhost and not vrahost:
        click.secho("Provide vcenterhost or vrahost or both",
                    bold=True)
        exit(0)

    if not billingaccount:
        click.secho('Billing Account needed for extraction, pass as -b or --billingaccount',
                    bold=True, fg='red')
        exit(0)

    if vcenterhost and not user or not password:
        click.secho("user or password cannot be left",
                    bold=True,fg='red')
        exit(0)

    if vrahost and not tenant:
        click.secho("tenant name needed for extracting from vra",
                    bold=True,fg="red")
        exit(0)
    months=kwargs.get('months',None)
    if not months:
        body['months'] = 1
        body['accounts'][0]['months'] = 1
    else:
        body['months']=int(months)
        body['accounts'][0]['months'] = int(months)

    body['accounts'][0]['billing_account_number']=billingaccount
    body['accounts'][0]['credentials']['vserver']=vcenterhost
    body['accounts'][0]['credentials']['username']=user
    body['accounts'][0]['credentials']['password']=password
    body['accounts'][0]['credentials']['tenant']=tenant

    return json.dumps(body)


@click.command()
@click.option('--filepath','-f',help='path of the config file',
              type=click.STRING)
@click.option('--vcenterhost','-c',help="vcenter host address",
              type=click.STRING)
@click.option('--vrahost','-r',help='vra host address',
              type=click.STRING)
@click.option('--user','-u',help='User name of vcenter',
              type=click.STRING)
@click.option('--password','-p',help='Password of user',
              type=click.STRING)
@click.option('--billingaccount','-b',help='Billing account for extraction',
              type=click.STRING)
@click.option('--tenant','-t',help='For extracting from vRA provide the tenant name',
              type=click.STRING)
@click.option('--extdir','-e',help='path for putting the gpd file',
              type=click.STRING)
@click.option('--months',"-m",help="Number of month to extract default 1",
              type=click.INT)
@click.option("--assetaccounts","-a",help="Assets account",
              type=click.STRING)
def main(*args,**kwargs):
    filepath=kwargs.get('filepath',None)
    extdir=kwargs.get('extdir',None)
    vcenterhost = kwargs.get("vcenterhost", None)
    vrahost = kwargs.get('vrahost', None)
    if not filepath and not vcenterhost and not vrahost:
        click.secho("usage cam_private --filename/-f --extdir/-e or"
                    "\ncam_private <vmware creds as [OPTIONS]>")
        exit(0)
    if not extdir:
        click.secho('ext dir needed for putting gpd file, pass as --extdir or -e',
                    fg="red", bold=True)
        exit(0)
        if not Path(extdir).exists():
            excmsg = 'extract directory [ ' + extdir + ' ] does not exist'
            raise EnvironmentError(excmsg)
    if filepath:
        body = json.load(open(filepath, 'r'))
        msgbody = json.dumps(body)

    else:
        msgbody = _create_json_from_command(*args,**kwargs)

    try:
        start_process_time = utils.now('%Y%m%d%H%M%S')
        logger = configure_logging('vmware.extract', start_process_time)
        logger.info('~~~~~~~~~~~~~~~~~~~~~~~~start of messaging~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        _config = utils.load()
        broker_config = _config['vmware']['broker']
        _work_dir = Path.getcwd()
        myclient = Client(_work_dir,logger)
        global envextdir
        envextdir = extdir
        myclient.callback(msgbody)
    except Exception as e:
        logger.error(traceback.format_exc())

if __name__=='__main__':
    main()