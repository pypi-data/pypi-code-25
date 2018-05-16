"""
#*===================================================================
#*
#* Licensed Materials - Property of IBM
#* IBM Cost And Asset Management
#* Copyright IBM Corporation 2017. All Rights Reserved.
#*
#*===================================================================
"""

from requests.exceptions import ConnectionError, ChunkedEncodingError,ReadTimeout,ConnectTimeout
from dateutil.relativedelta import relativedelta
from vmware.extract.strings import VMware_strings
from pandas.io.json import json_normalize
from vmware.extract.utils import retry
from vmware.extract import utils
from requests import Response
from os.path import basename
from functools import wraps
import logging.config
from path import Path
import pandas as pd
import traceback
import requests
import datetime
import logging
import time
import json
import glob
import pika
import os
import re
import csv
import datetime
import pytz
import os.path
from vmware.extract.serverinstance import ServerInstance as SI
#from pyVmomi import vmodl
from hurry.filesize import size



class Client:

    logger = logging.getLogger('{}'.format(
        __name__
    ))

    def __init__(self, workdir, tempdir, ch, props, envextdir,run_by=None):
        self._workdir = workdir
        self._tempdir = tempdir
        self._settings = utils._load_yaml('assets/conf.yaml')  # TODO: change the hardcoded path
        self._dateformat = self._settings['dateformat']
        self._start_time = utils.now('%Y%m%d%H%M%S')
        self._extractdate = utils.now(self._dateformat)
        self._ch = ch
        self._properties = props
        self.envextdir = Path(envextdir).makedirs_p()
        self._config = utils.load()
        self.deletetempfiles = self._config['vmware']['deletetempfiles']
        self.run_by=run_by

        self.logger.info('Work Dir :' + self._workdir)
        self.logger.info('Temp Dir :' + self._tempdir)
        self.logger.info('Start time : ' + self._start_time)

    def extract_assets_files(self, billingaccount, assetaccount, period):  # period only required in utilization
        # if we have asset accounts then asset account is vRA and billing account is vsphere
        if assetaccount['asset_account_number'] == 'default-asset-account':    #if the asset account is default then we get assets for vsphere which is the billing account number
            self.logger.info('asset account number is %s', assetaccount['asset_account_number'])
            asset_account_number = assetaccount['asset_account_number']
            billing_account_number = billingaccount['billing_account_number']
            dt = datetime.datetime.now()  # store asset data only in current month folder
            ym = dt.strftime("%Y%m")
            y_m = dt.strftime('%Y-%m')
            ym_extdir = self.envextdir / ym / self._settings['provider'] / billingaccount['billing_account_number'] / asset_account_number
            ym_extdir.makedirs_p()
            si = SI(billingaccount['vserver'], billingaccount['username'], billingaccount['password'])

            self.publish_progress(
                utils.reply_body('asset', billing_account_number, asset_account_number, VMware_strings.STATUS_EXTRACT_STARTED,
                                 y_m, "", "", ""),self.run_by)
            self.get_vms(si, billing_account_number, asset_account_number )  # get vm asset data
            self.get_datacenters(si, billing_account_number, asset_account_number)  # get datacenter  asset data
            self.get_hosts_and_datastore(si, billing_account_number, asset_account_number)  # get hosts and datastore
            # if execution reaches till here, it means extraction of all assets has succeeded , hence publish SUCCESS
            body = utils.reply_body('asset', billing_account_number, asset_account_number,
                                    VMware_strings.STATUS_EXTRACT_COMPLETED,
                                    period,
                                    requests.codes.ok,
                                    VMware_strings.RESPONSE_SUCCESS, "")
            self.publish_progress(body,self.run_by)
            # merge all pages data to single csv, and filter if any with regular expression :TODO explain arguments below in README
            gpd_file = Path(
                self._tempdir / self._settings['gpdfileformat'].format(asset_account_number, self._start_time, 'csv'))
            assetlist = ['VM', 'DC', 'DS', 'hosts']
            self.logger.info('list of assets to be obtained from provider %s', assetlist)
            asset_gpd_file = self.mergecsvs(asset_account_number, billing_account_number, gpd_file, None, None, assetlist)
            asset_zipfilename = Path(
                ym_extdir / self._settings['gpdfileformat'].format(asset_account_number, self._start_time, 'csv.zip'))
            asset_zip = utils.compress(asset_zipfilename, asset_gpd_file)
            if self.deletetempfiles:
                self.logger.debug("removing tempdir : %s", self._tempdir)
                utils.rmtree(self._tempdir)
            if asset_gpd_file and asset_zip:
                self.logger.info('Persisted asset data for account %s, in file %s', asset_account_number, asset_zip)
                return asset_zip
            else:
                return None
        else:
            # When vRA is present
            self.logger.info('asset account number is %s', assetaccount['asset_account_number'])
            asset_account_number = assetaccount['asset_account_number']
            billing_account_number = billingaccount['billing_account_number']
            dt = datetime.datetime.now()  # store asset data only in current month folder
            ym = dt.strftime("%Y%m")
            y_m = dt.strftime('%Y-%m')
            ym_extdir = self.envextdir / ym / self._settings['provider'] / billingaccount[
                'billing_account_number'] / asset_account_number
            ym_extdir.makedirs_p()
            si = SI(billingaccount['vserver'], billingaccount['username'], billingaccount['password'])

            self.publish_progress(
                utils.reply_body('asset', billing_account_number, asset_account_number, VMware_strings.STATUS_EXTRACT_STARTED,
                                 y_m, "", "", ""),self.run_by)
            self.get_vms(si, billing_account_number, asset_account_number)  # get vm asset data
            self.get_datacenters(si, billing_account_number, asset_account_number)  # get datacenter  asset data
            self.get_hosts_and_datastore(si, billing_account_number, asset_account_number)  # get hosts and datastore
            self.get_vms_vRA(billingaccount, assetaccount)
            # if execution reaches till here, it means extraction of all assets has succeeded , hence publish SUCCESS
            body = utils.reply_body('asset', billing_account_number, asset_account_number,
                                    VMware_strings.STATUS_EXTRACT_COMPLETED,
                                    period,
                                    requests.codes.ok,
                                    VMware_strings.RESPONSE_SUCCESS, "")
            self.publish_progress(body,self.run_by)
            # join csv's, this function will be used when you want to join values in created csv files
            self.joincsvs(asset_account_number, 'VM', 'VMvRA')
            # merge all pages data to single csv, and filter if any with regular expression :TODO explain arguments below in README
            gpd_file = Path(
                self._tempdir / self._settings['gpdfileformat'].format(asset_account_number, self._start_time, 'csv'))
            assetlist = ['VM', 'DC', 'DS', 'hosts','VMvRA']
            asset_gpd_file = self.mergecsvs(asset_account_number, billing_account_number, gpd_file, None, None, assetlist)
            asset_zipfilename = Path(
                ym_extdir / self._settings['gpdfileformat'].format(asset_account_number, self._start_time, 'csv.zip'))
            asset_zip = utils.compress(asset_zipfilename, asset_gpd_file)
            if self.deletetempfiles:
                self.logger.debug("removing tempdir : %s", self._tempdir)
                utils.rmtree(self._tempdir)
            if asset_gpd_file and asset_zip:
                self.logger.info('Persisted asset data for account %s, in file %s', asset_account_number, asset_zip)
                return asset_zip
            else:
                return None

    # Get VMs for 7.2 and 7.3 vRA
    def get_vms_vRA(self, billingaccount, assetaccount):
        asset_account_number = assetaccount['asset_account_number']
        billing_account_number = billingaccount['billing_account_number']

        vm_subs_asset_url = self._settings['urls']['vm'].format(assetaccount['vserver'])
        self.logger.info('VM asset url: %s', vm_subs_asset_url)
        fn = 'assets_VMvRA_{}_{}.json'.format(asset_account_number, self._start_time)
        asset_data = None
        try:
            asset_data = self.write_vmware_data(vm_subs_asset_url, assetaccount, fn)
            self.logger.info('processing VM asset data is complete')
        except (ConnectionError, ChunkedEncodingError, ReadTimeout, ConnectTimeout) as e:
            self.logger.error('max tries exceeded, error getting VM data from provider: %s', e)
            body = utils.reply_body('asset', billing_account_number, asset_account_number, VMware_strings.STATUS_EXTRACT_FAILED,
                                    '',
                                    '0', json.dumps(str(e)), "")
            self.publish_progress(body,self.run_by)
            raise Exception('retry API call to provider failed : ', vm_subs_asset_url)
        except Exception as ea:
            self.logger.error('error getting VM data from provider: %s', ea)
            body = utils.reply_body('asset', billing_account_number, asset_account_number, VMware_strings.STATUS_EXTRACT_FAILED,
                                    '',
                                    '0', json.dumps(str(ea)), "")
            self.publish_progress(body,self.run_by)
            raise Exception('Error getting VM data from provider : ', vm_subs_asset_url)
        if isinstance(asset_data, Response):  # only on error conditions from provider this is true
            body = utils.reply_body('asset', billing_account_number, asset_account_number, VMware_strings.STATUS_EXTRACT_FAILED,
                                    '',
                                    asset_data.status_code, asset_data.json(), "")
            self.publish_progress(body,self.run_by)
            raise Exception('API call to provider failed : ', vm_subs_asset_url)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~Get VMs ~~~~~~~~~~~~~~~~~~~~~~~~~~

    def get_vms(self, si, billingaccountnumber, assetaccountnumber):
        self.logger.info('get VM asset through sdk functions')
        fn = 'assets_VM_{}_{}.csv'.format(assetaccountnumber, self._start_time)
        csvfname = Path(self._tempdir) / fn
        try:
            vmdict = si.get_registered_vms()
            l1 = []
            for k, v in vmdict.iteritems():
                d1= {}
                capacityText = {}
                assetDetail = {}
                url = ''
                summary = k.summary
                d1.update({'providerAssetId':summary.config.instanceUuid})
                d1.update({'assetName':summary.config.name})
                d1.update({'assetType':'VirtualMachine'})
                capacityText['memorySizeMB'] = str(summary.config.memorySizeMB)
                capacityText['numCpu'] = str(summary.config.numCpu)
                capacityText['storage'] = str(summary.storage.committed)
                d1.update({'capacityText':json.dumps(capacityText)})
                d1.update({'tags':summary.config.annotation})
                d1.update({'operationalState':summary.runtime.powerState})
                assetDetail['Bios UUID'] = str(summary.config.uuid)
                assetDetail['uptimeSeconds'] = str(summary.quickStats.uptimeSeconds)
                assetDetail['maxMemoryUsage'] = str(summary.runtime.maxMemoryUsage)
                assetDetail['maxCpuUsage'] = str(summary.runtime.maxCpuUsage)
                assetDetail['numVirtualDisks'] = str(summary.config.numVirtualDisks)
                if summary.guest is not None:
                    ip_address = summary.guest.ipAddress
                    tools_version = summary.guest.toolsStatus
                    if tools_version is not None:
                        assetDetail['VMware-tools'] = str(tools_version)
                    if ip_address:
                        url = ip_address
                d1.update({'providerApiText':assetDetail})
                d1.update({'assetAccountId':assetaccountnumber})
                d1.update({'url':url})
                l1.append(d1)
            df = pd.DataFrame(l1)
            df['assetStartDate']=''
            df['extractDate'] = ''
            df['providerName'] = ''
            df['assetEndDate']=''
            df['assetCreatedBy']=''
            df['assetEndedBy']=''
            df['linkedAssetId']=''
            df['billingAccountId']=''
            df['providerRegionCode']=''
            df['orderId']=''
            df['correlationAssetId']=''
            df['assetSource'] = 'asset'
            df['attributes'] = ''
            df.to_csv(csvfname, encoding='utf-8')
            self.logger.info('processing VM asset data is complete')

        except (ConnectionError, ChunkedEncodingError, ReadTimeout, ConnectTimeout) as e:
            self.logger.error('max tries exceeded, error getting VM data from provider: %s', e)
            body = utils.reply_body('asset', billingaccountnumber, assetaccountnumber, VMware_strings.STATUS_EXTRACT_FAILED, '',
                                    '0', json.dumps(str(e)), "")
            self.publish_progress(body,self.run_by)
            raise Exception('retry SDK function call to provider failed')
        except Exception as ea:
            self.logger.error('error getting VM data from provider: %s', ea)
            body = utils.reply_body('asset', billingaccountnumber, assetaccountnumber, VMware_strings.STATUS_EXTRACT_FAILED, '',
                                '0', json.dumps(str(ea)), "")
            self.publish_progress(body,self.run_by)
            raise Exception('Error getting VM data from provider')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~DataCenter~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_datacenters(self, si, billingaccountnumber, assetaccountnumber):
        self.logger.info('get datacenter asset through sdk functions')
        fn = 'assets_DC_{}_{}.csv'.format(assetaccountnumber, self._start_time)
        csvfname = Path(self._tempdir) / fn
        try:
            dcdict = si.get_datacenters()
            l1 = []
            for k, v in dcdict.iteritems():
                d1 = {}
                assetDetail = []
                d1.update({'assetName': k.name})
                d1.update({'assetType':'Datacenter'})
                assetDetail.append("datastoreFolder:" + str(k.datastoreFolder))
                assetDetail.append("hostFolder:" + str(k.hostFolder))
                assetDetail.append("networkFolder:" + str(k.networkFolder))
                assetDetail.append("parent:" + str(k.parent))
                assetDetail.append("vmFolder:" + str(k.vmFolder))
                d1.update({'providerApiText': assetDetail})
                d1.update({'assetAccountId': assetaccountnumber})
                l1.append(d1)
            df = pd.DataFrame(l1)
            df['providerAssetId'] = ''
            df['extractDate'] = ''
            df['providerName'] = ''
            df['tags'] = ''
            df['url'] = ''
            df['capacityText'] = ''
            df['operationalState'] = 'ON'   #TODO: check if we can do this always
            df['assetStartDate'] = ''
            df['assetEndDate'] = ''
            df['assetCreatedBy'] = ''
            df['assetEndedBy'] = ''
            df['linkedAssetId'] = ''
            df['billingAccountId'] = ''
            df['providerRegionCode'] = ''
            df['orderId'] = ''
            df['correlationAssetId'] = ''
            df['assetSource'] = ''
            df['attributes'] = ''
            df.to_csv(csvfname, encoding='utf-8')
            self.logger.info('processing VM asset data is complete')

        except (ConnectionError, ChunkedEncodingError, ReadTimeout, ConnectTimeout) as e:
            self.logger.error('max tries exceeded, error getting VM data from provider: %s', e)
            body = utils.reply_body('asset', billingaccountnumber, assetaccountnumber, VMware_strings.STATUS_EXTRACT_FAILED,
                                    '',
                                    '0', json.dumps(str(e)), "")
            self.publish_progress(body,self.run_by)
            raise Exception('retry SDK function call to provider failed')
        except Exception as ea:
            self.logger.error('error getting VM data from provider: %s', ea)
            body = utils.reply_body('asset', billingaccountnumber, assetaccountnumber, VMware_strings.STATUS_EXTRACT_FAILED,
                                    '',
                                    '0', json.dumps(str(ea)), "")
            self.publish_progress(body,self.run_by)
            raise Exception('Error getting VM data from provider')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~NICs~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_hosts_and_datastore(self, si, billingaccountnumber, assetaccountnumber):
        self.logger.info('get hosts and datastore asset through sdk functions')
        fn1 = 'assets_hosts_{}_{}.csv'.format(assetaccountnumber, self._start_time)
        csvfname1 = Path(self._tempdir) / fn1
        fn2 = 'assets_DS_{}_{}.csv'.format(assetaccountnumber, self._start_time)
        csvfname2 = Path(self._tempdir) / fn2
        try:
            dcdict = si.get_hosts()
            l1 = []
            for k, v in dcdict.iteritems():
                d1 = {}
                d1.update({'assetName': k.name})
                d1.update({'assetType':'ESXi Host'})
                d1.update({'assetAccountId': assetaccountnumber})
                l1.append(d1)
            df1 = pd.DataFrame(l1)
            df1['providerAssetId'] = ''
            df1['extractDate'] = ''
            df1['providerName'] = ''
            df1['providerApiText'] = ''
            df1['tags'] = ''
            df1['url'] = ''
            df1['capacityText'] = ''
            df1['operationalState'] = 'ON'   #TODO: check if we can do this always
            df1['assetStartDate'] = ''
            df1['assetEndDate'] = ''
            df1['assetCreatedBy'] = ''
            df1['assetEndedBy'] = ''
            df1['linkedAssetId'] = ''
            df1['billingAccountId'] = ''
            df1['providerRegionCode'] = ''
            df1['orderId'] = ''
            df1['correlationAssetId'] = ''
            df1['assetSource'] = ''
            df1['attributes'] = ''
            df1.to_csv(csvfname1, encoding='utf-8')

            # Datastorage
            l2=[]
            for k, v in dcdict.iteritems(): # we can get data from same host content
                storage_system = k.configManager.storageSystem
                host_file_sys_vol_mount_info = storage_system.fileSystemVolumeInfo.mountInfo
                # Map all filesystems
                for host_mount_info in host_file_sys_vol_mount_info:
                    d2 = {}
                    # Extract only VMFS volumes
                    if host_mount_info.volume.type == "VMFS":
                        extents = host_mount_info.volume.extent
                        d2.update({'assetName': host_mount_info.volume.name})
                        d2.update({'assetType': 'Datastore'})
                        d2.update({'assetAccountId': host_mount_info.volume.uuid})
                        capacityText = []
                        capacityText.append("storage : " + size(host_mount_info.volume.capacity))
                        d2.update({'capacityText': capacityText})
                        assetDetail = []
                        assetDetail.append("VMFS Version: " + str(host_mount_info.volume.version))
                        assetDetail.append("Is Local VMFS: " + str(host_mount_info.volume.local))
                        assetDetail.append("SSD: " + str(host_mount_info.volume.ssd))
                        d2.update({'providerApiText': assetDetail})
                        l2.append(d2)
            df2 = pd.DataFrame(l2)
            df2['providerAssetId'] = ''
            df2['extractDate'] = ''
            df2['providerName'] = ''
            df2['providerApiText'] = ''
            df2['tags'] = ''
            df2['url'] = ''
            df2['operationalState'] = 'ON'   #TODO: check if we can do this always
            df2['assetStartDate'] = ''
            df2['assetEndDate'] = ''
            df2['assetCreatedBy'] = ''
            df2['assetEndedBy'] = ''
            df2['linkedAssetId'] = ''
            df2['billingAccountId'] = ''
            df2['providerRegionCode'] = ''
            df2['orderId'] = ''
            df2['correlationAssetId'] = ''
            df2['assetSource'] = ''
            df2['attributes'] = ''
            df2.to_csv(csvfname2, encoding='utf-8')

            self.logger.info('processing hosts asset data is complete')
        except (ConnectionError, ChunkedEncodingError, ReadTimeout, ConnectTimeout) as e:
            self.logger.error('max tries exceeded, error getting nic data from provider: %s', e)
            body = utils.reply_body('asset', billingaccountnumber, assetaccountnumber, VMware_strings.STATUS_EXTRACT_FAILED, '',
                                    '0', json.dumps(str(e)), "")
            self.publish_progress(body,self.run_by)
            raise Exception('retry SDK function call to provider failed')
        except Exception as ea:
            self.logger.error('error getting nic data from provider: %s', ea)
            body = utils.reply_body('asset', billingaccountnumber, assetaccountnumber, VMware_strings.STATUS_EXTRACT_FAILED, '',
                                '0', json.dumps(str(ea)), "")
            self.publish_progress(body,self.run_by)
            raise Exception('Error getting nic data from provider')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~WRITE - TO - FILE~~~~~~~~~~~~~~~~~~~~~~~~~~
    @retry((ConnectionError, ChunkedEncodingError, ReadTimeout, ConnectTimeout), tries=8, delay=1, backoff=2,
           logger=logger)
    def write_vmware_data(self, url, account, fn, writetocsv=True):
        # prepare headers from conf file , headers = {'Authorization': 'bearer ' + api_key_value}
        key = self._settings['reqheaders']['key']
        val = self._settings['reqheaders']['value'] + " " + account['api_key']
        headers = {key: val}
        try:
            r = requests.get(url, headers=headers, verify=False)
            self.logger.debug('response message: %s', r.json())
            #TODO: implement nextpage when page data crosses 1000
            # retry if the response error code is 401 : ExpiredAuthenticationToken
            if r.status_code == 401 and r.json()['error']['code'] == 'ExpiredAuthenticationToken':
                self.logger.info('retrying with new key since the error code is 401 : ExpiredAuthenticationToken')
                tenant_id = account['tenant_id']
                application_id = account['application_id']
                application_secret = account['application_secret']

                api_key = utils.get_vmware_token(account)  # generate token
                account['api_key'] = api_key  # This will change the key globally for account

                key = self._settings['reqheaders']['key']
                val = self._settings['reqheaders']['value'] + " " + api_key
                headers = {key: val}
                r = requests.get(url, headers=headers)
                if r.status_code != requests.codes.ok:
                    self.logger.error('retry response code  is %d and response is %s', r.status_code, r.json())
                    raise Exception('retry API call to provider failed : ', url)
            if r.status_code == 429 and r.json()['error']['code'] == 'SubscriptionRequestsThrottled':
                matches = re.search(r'.*Please try again after (.*) (.*).', r['error']['message'])
                timetowait = utils.get_timeout(matches)
                self.logger.info('Error code is %s , hence retrying with new key after waiting for %s secs',
                                 'SubscriptionRequestsThrottled', timetowait)
                time.sleep(timetowait)
                # instead of checking if token has expired, we will anyway create a new token as these timeout's will be large
                api_key = utils.get_vmware_token(account)  # generate token
                account['api_key'] = api_key  # This will change the key globally for account

                key = self._settings['reqheaders']['key']
                val = self._settings['reqheaders']['value'] + " " + api_key
                headers = {key: val}
                r = requests.get(url, headers=headers)
                if r.status_code != requests.codes.ok:
                    self.logger.error('retry response code  is %d and response is %s', r.status_code, r.json())
                    raise Exception('retry API call to provider failed : ', url)
            if r.status_code == 202 and r.json()['error']['code'] == 'ProcessingNotCompleted':
                matches = re.search(r'.*Please try again in (.*) (.*).', r.json()['error']['message'])
                timetowait = utils.get_timeout(matches, self._settings['timeout']['provider'])
                self.logger.info('Error code is %s , hence retrying with new key after waiting for %s secs',
                                 'ProcessingNotCompleted', timetowait)
                time.sleep(timetowait)
                # instead of checking if token has expired, we will anyway create a new token as these timeout's will be large
                api_key = utils.get_vmware_token(account)  # generate token
                account['api_key'] = api_key  # This will change the key globally for account

                key = self._settings['reqheaders']['key']
                val = self._settings['reqheaders']['value'] + " " + api_key
                headers = {key: val}
                r = requests.get(url, headers=headers)
                if r.status_code != requests.codes.ok:
                    self.logger.error('retry response code  is %d and response is %s', r.status_code, r.json())
                    raise Exception('retry API call to provider failed : ', url)
            if r.status_code != requests.codes.ok:
                self.logger.error('response code  is %d and response is %s', r.status_code, r.json())
                return r

            output = r.json()
            self.logger.debug('request url : %s', url)
            if writetocsv:
                with open(Path(self._tempdir) / fn, 'w+') as outfile:  # create a json file of response
                    json.dump(output, outfile)
                    outfile.close()
                with open(Path(self._tempdir) / fn) as csvfile:  # create the csv file later, here its just a file
                    data = json.load(csvfile)
                # Below for loop is for tags column, where we want tags value be kept as json and not as individual
                # columns of each tag
                # data is a dictionary above with values as {"value": [{},{},....{}]}

                #TODO: remove below comment when we get tags
                '''
                for k, v in data.iteritems():
                    for l1 in data[k]:
                        if 'tags' not in l1:  # cam-2242, add tags column if its not present in provider data
                            l1['tags'] = str('')  # cam-3056, sometimes gives Typeerror for this
                        else:
                            for k1, v1 in l1.iteritems():
                                tmpd = []
                                if k1 == "tags":
                                    d1 = l1[k1]
                                    for k2, v2 in d1.iteritems():
                                        d2 = {}
                                        d2[k2] = v2
                                        tmpd.append(d2)
                                    l1[k1] = tmpd
                '''
                se = pd.Series(data['content']) # required for providerApiText field, we get the json of each asset here
                df1 = json_normalize(data['content'])  # TODO: check if value always or resource may also come
                csvfname = Path(self._tempdir) / os.path.splitext(basename(csvfile.name))[0] + '.csv'
                self.logger.debug('csv filename : %s', csvfname)
                if not se.empty:  # if there are no values returned, don't add this field too
                    df1['providerApiText'] = se.values
                df1.to_csv(csvfname, index=False)
            return output
        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~join csvs~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def joincsvs(self,asset_account_number, leftasset, rightasset):
        dfleft = pd.DataFrame()
        dfright = pd.DataFrame()
        fnleft = 'assets_' + leftasset + '_{}_{}.csv'.format(asset_account_number, self._start_time)
        fnright = 'assets_' + rightasset + '_{}_{}.csv'.format(asset_account_number, self._start_time)
        self.logger.info('files to join %s, %s', fnleft,fnright)
        try:
            dfleft = pd.read_csv(self._tempdir / fnleft, index_col=None)
            dfright = pd.read_csv(self._tempdir / fnright, index_col=None)
        except pd.errors.EmptyDataError:
            self.logger.info('There are no values in left or right join csv files: %s or %s', fnleft, fnright)
        merged = pd.merge(dfleft, dfright, how = 'left', left_on = 'assetName', right_on = 'name')
        merged = merged.drop('assetStartDate',1)
        merged = merged.rename(columns={'dateCreated':'assetStartDate'})
        merged.to_csv(Path(self._tempdir) / fnleft, index=False, columns=list(dfleft))
        os.remove(Path(self._tempdir)/fnright) if os.path.exists(Path(self._tempdir)/fnright) else None

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~merge all csv files created ~~~~~~~~~~~~~~~~~~~~~~~~~~
    def mergecsvs(self,asset_account_number, billingaccount, gpd_file, colnames, regex, assetlist):
        try:
            dflist = []
            self.logger.info('merging all asset csv files to single csv')
            self.logger.info('list of assets to be merged %s', assetlist)
            for stype in assetlist:
                dictfname = self._settings['columns'][stype]
                d1 = {}
                for k, v in dictfname.iteritems():
                    if v is not None:
                        d1[k] = v
                d2 = {y: x for x, y in d1.iteritems()}  # Reverse key - values, this is needed when renaming columns
                fn = 'assets_' + stype + '_{}_{}.csv'.format(asset_account_number, self._start_time)
                self.logger.info('column values from conf file %s for asset %s', d1.values(),stype)
                if d1.values() == ['headers']:  #if you don't require any column mapping from conf yaml, match it to headers field in conf file
                    header = self._settings['headers'].split()
                else:
                    header = d1.values()
                self.logger.debug('header from conf.yaml file : %s', header)
                for fname in glob.glob(self._tempdir / fn):  # Name of asset csv file
                    self.logger.debug('asset csv filename : %s', fname)
                    df2 = pd.DataFrame()
                    try:
                        df2 = pd.read_csv(fname, index_col=None, usecols=header)
                    except pd.errors.EmptyDataError:
                        self.logger.info('There are no values in the %s csv file', fname)
                    df2.rename(columns=d2, inplace=True)  # Rename columns with the GPD columns
                    dflist.append(df2)
            # get headers from the yaml file and convert to list using split()
            cols = self._settings['headers'].split()
            self.logger.debug('columns from yaml file : %s', cols)
            dfo = pd.DataFrame(columns=cols)
            dfo.to_csv(Path(self._tempdir / 'output.csv'))
            # Append the above GPD blank dataframe to the asset dataframes to get NULL value in other columns
            dflist.append(dfo)

            # concat all dataframes in horizontal axis
            merged = pd.concat(dflist, axis=0)
            # update required columns with generated/derived data
            merged['providerName'] = self._settings['provider']
            merged['extractDate'] = self._extractdate
            merged['assetAccountId'] = asset_account_number
            merged['billingAccountId'] = billingaccount
            merged['assetStartDate'] = pd.to_datetime(merged['assetStartDate']).apply(lambda x: x.strftime(self._dateformat)if not pd.isnull(x) else '')
            merged['assetEndDate'] = pd.to_datetime(merged['assetEndDate']).apply(lambda x: x.strftime(self._dateformat)if not pd.isnull(x) else '')
            merged.loc[merged.tags == "[]", 'tags']= ''     #when no tags are present make it null, to be consistent with cost tags
            merged['tags'].replace(r"u\'(.+?)\'",'"\\1"', inplace=True, regex=True)
            merged['providerApiText'].replace(r"u\'(.+?)\'",'"\\1"', inplace=True, regex=True)
            if colnames is not None and regex is not None:
                self.logger.info('column names %s, regex %s, regex key %s, regex val %s', colnames, regex, regex[0].keys()[0],
                                 regex[0].values()[0])
                for assetcols in colnames:
                    self.logger.info('column name = %s',assetcols)
                    merged[assetcols].replace((regex[0].keys())[0], (regex[0].values())[0], inplace=True, regex=True)
            merged.to_csv(gpd_file, columns=cols, index=False) #removing quoting , fix for cam-2557

            return gpd_file
        except Exception as e:
            self.logger.error('error in merging assets csv files')
            self.logger.error(traceback.format_exc())
            raise

    def publish_progress(self, message,run_by=None):
        self.logger.debug('message to publish : %s', message)
        if run_by == 'cmd':
            self.logger.info(message)
        else:
            try:
                self.publish_message(message)
            except: # on connection closed reconnect and publish the message again
                self.logger.info('Got exception when trying to publish message, reconnecting')
                self._ch = utils.create_connection()
                self.publish_message(message)

    def publish_message(self, message):
        self._ch.basic_publish(exchange='', routing_key=self._properties.reply_to,
            properties=pika.BasicProperties(correlation_id=self._properties.correlation_id),body=str(message))