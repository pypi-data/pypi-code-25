import unittest
import mock
from vmware.extract.assets.client import Client as AssetClient
from path import Path
import os
import logging
from shutil import copy2
import glob
import re
import vmware.tests.mock_for_asset as mock_asset
import csv



class AssetTestCase(unittest.TestCase):

    def setUp(self):
        self.pwd = Path.getcwd()
        self.workdir = self.pwd / 'test'
        self.tempdir = self.workdir / 'tmp'
        self.envextdir = self.workdir / 'ext'
        os.chdir(self.pwd / 'packages' / 'vmware-extract' / 'vmware' / 'extract' )
        self.assetclient = AssetClient(self.workdir, self.tempdir, None, None,self.envextdir)
        os.chdir(Path(self.pwd))
        logging.basicConfig(level=logging.DEBUG,
                                     format='%(asctime)s %(levelname)s %(message)s',
                                     filename=Path('{}_{}.log'.format(__name__, self.assetclient._start_time)),
                                     filemode='w')
        self.si = None
        self.billingaccount = '000000'

    def tearDown(self):
        self.assetclient = None

    @mock.patch('requests.get',
                side_effect=mock_asset.MockAsset.mock_azure_write_data_exception)
    @mock.patch('vmware.extract.utils.create_connection',
                side_effect=mock_asset.MockAsset.mock_utils_create_connection)
    @mock.patch('vmware.extract.assets.client.Client.publish_message',
                side_effect=mock_asset.MockAsset.mock_publish_message)
    def test_get_vms_exception_handled(self,mock_client,mock_client2,mock_client3):
        with self.assertRaises(Exception) as exp:
            self.assetclient.get_vms_dummy(self.si,'bill123456','asset123456')

    @mock.patch('requests.get',
                side_effect=mock_asset.MockAsset.mock_azure_write_data_exception)
    @mock.patch('vmware.extract.utils.create_connection',
                side_effect=mock_asset.MockAsset.mock_utils_create_connection)
    @mock.patch('vmware.extract.assets.client.Client.publish_message',
                side_effect=mock_asset.MockAsset.mock_publish_message)
    def test_get_storage_accounts_exception_handled(self,mock_client,mock_client2,mock_client3):
        with self.assertRaises(Exception) as exp:
            self.assetclient.get_datacenters(self.si,self.billingaccount)


    @mock.patch('requests.get',
                side_effect=mock_asset.MockAsset.mock_azure_write_data_exception)
    @mock.patch('vmware.extract.utils.create_connection',
                side_effect=mock_asset.MockAsset.mock_utils_create_connection)
    @mock.patch('vmware.extract.assets.client.Client.publish_message',
                side_effect=mock_asset.MockAsset.mock_publish_message)
    def test_get_nws_exception_handled(self,mock_client,mock_client2,mock_client3):
        with self.assertRaises(Exception) as exp:
            self.assetclient.get_hosts_and_datastore(self.si, self.billingaccount)


    '''
    @mock.patch('requests.get', side_effect=mock_asset.MockAsset.mock_azure_url_expired_auth)
    @mock.patch('vmware.extract.utils.get_azure_token', side_effect=mock_asset.MockAsset.mock_utils_get_azure_token)
    def test_write_azure_data_fail_auth_expired(self , mock_client,mock_client2):
        headers = {'Authorization': 'bearer ' + '000000'}
        url = 'https://management.vmware.com/subscriptions/000000/providers/Microsoft.Compute/virtualmachines?api-version=2016-04-30-preview'
        fn = 'assets.json'
        with self.assertRaises(Exception) as exp:
            self.assetclient.write_azure_data(url, self.d1, fn)
        self.assertRegexpMatches(str(exp.exception),"retry API call to provider failed : .*")

    
    @mock.patch('requests.get', side_effect=mock_asset.MockAsset.mock_azure_url_resource_not_found)
    def test_write_azure_data_fail_auth_expired(self, mock_client):
        headers = {'Authorization': 'bearer ' + '000000'}
        url = 'https://management.vmware.com/subscriptions/000000/providers/Microsoft.Compute/virtualmachines?api-version=2016-04-30-preview'
        fn = 'assets.json'
        with self.assertRaises(Exception):
            self.assetclient.write_azure_data(url, self.d1, fn)

    @unittest.skip("This is old")
    def test_mergecsvs(self):
        os.chdir(Path(self.pwd))
        fn = 'assets_' + '*.csv'
        for fname in glob.glob(Path('testdata') / fn):
            copy2(fname,self.pwd)
        for fname in glob.glob(fn):
            s = re.sub(r'assets_(.*)_(.*)_(.*).csv', r'assets_\1_\2_' + self.assetclient._start_time + '.csv', fname)
            os.rename(fname,s)
        self.assetclient.mergecsvs('123456', None, None)
        for fname in glob.glob(fn):
            os.remove(fname)
        mf = 'merged_123456_' + self.assetclient._start_time + '.csv'
        numoflines = open(mf).read().count('\n')
        logging.debug("Number of line in merged csv = %d", numoflines)
        self.assertEqual(numoflines,736)
        os.remove(mf)
        os.remove('output.csv')
    '''
    def test_gpd_columns(self):
        self.tempdir.makedirs_p()
        file_path = Path(self.pwd / 'packages' / 'vmware-extract' / 'vmware' /'tests'/ 'testdata')
        fn = file_path/'assets_' + '*.csv'
        for fname in glob.glob(fn):
            copy2(fname, self.tempdir)
        for fname in glob.glob(self.tempdir/'assets_' + '*.csv'):
            s = re.sub(r'assets_(.*)_(.*)_(.*).csv', r'assets_\1_\2_' + self.assetclient._start_time + '.csv', fname)
            os.rename(fname, s)
        yaml_headers = self.assetclient._settings['headers'].split()
        file_path = Path(self.pwd / 'packages' / 'vmware-extract' / 'vmware' /'tests'/ 'testdata')
        gpd_file = file_path / 'asset-gpd.csv'
        gpd = self.assetclient.mergecsvs('12345',self.billingaccount, gpd_file, None, None, ['VM'])
        with open(gpd_file, 'r') as f:
            d_reader = csv.DictReader(f)
            headers = d_reader.fieldnames
        self.assertEquals(yaml_headers,headers)
        for fname in glob.glob(self.tempdir/'*.csv'):
            os.remove(fname)
        os.removedirs(self.tempdir)

    @mock.patch('pika.channel.Channel.basic_publish',
                side_effect=mock_asset.MockAsset.mock_ch_basic_publish_exception)
    def test_publish_message_fail(self, mock_client1):
        with self.assertRaises(Exception):
            self.assetclient.publish_message("Test Message")

    @mock.patch('pika.channel.Channel.basic_publish',
                side_effect=mock_asset.MockAsset.mock_ch_basic_publish_exception)
    def test_publish_progress_fail(self, mock_client1):
        with self.assertRaises(Exception):
            self.assetclient.publish_message("Test Message")



