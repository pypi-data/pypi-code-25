import unittest
import mock
from vmware.extract.utilization.client import Client as UtilizationClient
from path import Path
import os
import logging
from shutil import copy2
from vmware.extract import utils
import glob
import re
import vmware.tests.mock_for_asset as mock_asset
import requests

@unittest.skip("convert to vmware tests")
class AssetTestCase(unittest.TestCase):
    def setUp(self):
        self.pwd = Path.getcwd()
        self.workdir = self.pwd / 'test'
        self.tempdir = self.workdir / 'tmp'
        self.envextdir = self.workdir / 'ext'
        os.chdir(self.pwd / 'packages' / 'vmware-extract' / 'vmware' / 'extract')
        self.utilizationclient = UtilizationClient(self.workdir, self.tempdir, None, None,self.envextdir)
        os.chdir(Path(self.pwd))
        logging.basicConfig(level=logging.DEBUG,
                                     format='%(asctime)s %(levelname)s %(message)s',
                                     filename=Path('{}_{}.log'.format(__name__, self.utilizationclient._start_time)),
                                     filemode='w')
        self.d1 = {'tenant_id': 't12345', 'application_id': 'a12345', 'application_secret': 's12345',
                  'asset_account_number': '12345', 'api_key': 'dummy_key'}
        self.billingaccount = '000000'


    def tearDown(self):
        self.utilizationclient = None

    def test__load_yaml(self):
        self.assertEqual(self.utilizationclient._settings.keys(), ['utilization_prefix', 'dateformat', 'headers', 'reqheaders', 'apivars', 'urls', 'provider', 'gpdfileformat', 'columns'])

    @mock.patch('requests.get',
                side_effect=mock_asset.MockAsset.mock_azure_write_data_exception)
    @mock.patch('vmware.extract.utils.create_connection',
                side_effect=mock_asset.MockAsset.mock_utils_create_connection)
    @mock.patch('vmware.extract.utilization.client.Client.publish_message',
                side_effect=mock_asset.MockAsset.mock_publish_message)
    def test_get_utilization_data(self, mock_client1, mock_client2, mock_client3):
        headers = {'Authorization': 'bearer ' + '000000'}

        with self.assertRaises(Exception) as exp:
            self.utilizationclient.get_utilization_data(self.d1, 1,self.billingaccount)





    @mock.patch('requests.get', side_effect=mock_asset.MockAsset.mock_azure_url_expired_auth)
    @mock.patch('vmware.extract.utils.get_azure_token', side_effect=mock_asset.MockAsset.mock_utils_get_azure_token)
    def test_write_azure_data_fail_auth_expired(self, mock_client, mock_client2):
        headers = {'Authorization': 'bearer ' + '000000'}
        url = 'https://management.vmware.com/subscriptions/000000/providers/Microsoft.Compute/virtualmachines?api-version=2016-04-30-preview'
        fn = 'utilization.json'
        with self.assertRaises(Exception) as exp:
            self.utilizationclient.write_azure_data(url, self.d1, fn)
        self.assertRegexpMatches(str(exp.exception), "retry API call to provider failed : .*")

    @mock.patch('requests.get', side_effect=mock_asset.MockAsset.mock_azure_url_resource_not_found)
    def test_write_azure_data_fail_auth_expired(self, mock_client):
        headers = {'Authorization': 'bearer ' + '000000'}
        url = 'https://management.vmware.com/subscriptions/000000/providers/Microsoft.Compute/virtualmachines?api-version=2016-04-30-preview'
        fn = 'utilization.json'
        with self.assertRaises(Exception):
            self.utilizationclient.write_azure_data(url,self.d1, fn)

    @unittest.skip("Old test case")
    def test_mergecsvs(self):
        os.chdir(Path(self.pwd))
        fn = 'utilization_' + '*.csv'
        for fname in glob.glob(Path('testdata') / fn):
            copy2(fname,self.pwd)
        for fname in glob.glob(fn):
            s = re.sub(r'utilization_(.*)_(.*)_(.*).csv', r'utilization_\1_' + self.utilizationclient._start_time + '_\\3.csv', fname)
            os.rename(fname,s)
        self.utilizationclient.mergecsvs('123456', None, None)
        for fname in glob.glob(fn):
            os.remove(fname)
        mf = 'merged_123456_' + self.utilizationclient._start_time + '.csv'
        numoflines = open(mf).read().count('\n')
        logging.debug("Number of line in merged csv = %d", numoflines)
        self.assertEqual(numoflines,6001)
        os.remove(mf)
        os.remove('output.csv')

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
