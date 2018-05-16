import unittest
import mock
from mock import patch
from vmware.extract.cost.client import CostClient
from path import Path
import yaml
import vmware.tests.mock_cost_client as mock_client
import csv
from requests import Response
import os
import glob
import pandas


class Test_cost_vmware(unittest.TestCase):
    """
        Unit Test class for Azure Cost Extractor
    """

    @mock.patch('vmware.extract.utils._load_yaml', side_effect=mock_client.MockCost.mock_load_yaml)
    @mock.patch('vmware.extract.utils.load', side_effect=mock_client.MockCost.mock_load)
    @mock.patch('path.Path', side_effect=mock_client.MockCost.mocked_path)
    def setUp(self, mock_load_yaml, mock_load, mocked_path):

        self._dateformat = '%Y-%m-%d %H:%M:%S.%f'
        self._workdir = Path.getcwd()
        self._tempdir = 'tmp'
        self._ch = 'mock-channel'
        self._properties = mock_client.Properties()
        self.envextdir = 'tmp/cost/test/envextdir'
        self.deletetempfiles = True
        self.cost_client = CostClient(self._workdir,self._tempdir, self._ch, self._properties, self.envextdir)

    def tearDown(self):
        self.cost_client = None

    @mock.patch('vmware.extract.cost.client.CostClient.publish_message',
                side_effect=mock_client.MockCost.mocked_publish_message_exception)
    def test_publish_message_fail(self, mock_client1):
        with self.assertRaises(Exception):
            self.cost_client.publish_message("Test Message")

    @mock.patch('pika.channel.Channel.basic_publish',
                side_effect=mock_client.MockCost.mock_basic_publish_exception)
    def test_publish_progress_fail(self, mock_client1):
        with self.assertRaises(Exception):
            self.cost_client.publish_progress("Test Message")

    @mock.patch('pika.channel.Channel.basic_publish',
                side_effect=mock_client.MockCost.mock_publish_progress)
    def test_publish_progress(self, mock_client1):
        self.cost_client.publish_progress("Test Message", "cmd")

    @mock.patch('vmware.extract.utils._load_yaml', side_effect=mock_client.MockCost.mock_load_rate_card_config)
    @mock.patch('vmware.extract.utils.load', side_effect=mock_client.MockCost.mock_load)
    @mock.patch('json.load', side_effect=mock_client.MockCost.mock_exception)
    def test_extract_cost_files(self, mock_load_yaml, mock_load, mock_except):

        _account_number='mock_account_number'
        creds={
                    'vserver':'mock_vserver',
                     'username':'mock_user_name',
                     'password':'mock_password'
               }
        period=1

        self.cost_client.extract_cost_files(_account_number, creds, period)

    @mock.patch('vmware.extract.utils._load_yaml', side_effect=mock_client.MockCost.mock_load_rate_card_config_for_complex_type)
    @mock.patch('vmware.extract.utils.load', side_effect=mock_client.MockCost.mock_load)
    @mock.patch('json.load', side_effect=mock_client.MockCost.mock_exception)
    def test_extract_cost_files1(self, mock_load_yaml, mock_load, mock_except):

        _account_number='mock_account_number'
        creds={
                    'vserver':'mock_vserver',
                     'username':'mock_user_name',
                     'password':'mock_password'
               }
        period=1

        self.cost_client.extract_cost_files(_account_number, creds, period)

    @mock.patch('vmware.extract.utils._load_yaml',
                side_effect=mock_client.MockCost.mock_load_rate_card_config1)
    @mock.patch('vmware.extract.utils.load', side_effect=mock_client.MockCost.mock_load)
    @mock.patch('json.load', side_effect=mock_client.MockCost.mock_exception)
    def test_extract_cost_files2(self, mock_load_yaml, mock_load, mock_except):
        _account_number = 'mock_account_number'
        creds = {
            'vserver': 'mock_vserver',
            'username': 'mock_user_name',
            'password': 'mock_password'
        }
        period = 1

        self.cost_client.extract_cost_files(_account_number, creds, period)

    def test_get_currency_from_rate_card(self):
        rate_card_json_data =  [
                 {
                    "policy_type": "Compute",
                    "name": "broker_egl@vsphere.local",
                    "unit_of_measure": "Per vCPU",
                    "unit_cost": 0.5,
                    "currency": "USD"
                },
                {
                    "policy_type": "Compute",
                    "name": "broker_egl@vsphere.local",
                    "unit_of_measure": "Per GB",
                    "unit_cost": 0.5,
                    "currency": "USD"
                },
                {
                    "policy_type": "Storage",
                    "name": "broker_egl@vsphere.local",
                    "unit_of_measure": "Per GB",
                    "unit_cost": 0.5,
                    "currency": "USD"
                }
            ]
        policy_type = "Compute"
        unit_of_measure = "Per vCPU"
        self.cost_client.get_currency_from_rate_card(rate_card_json_data, policy_type, unit_of_measure)

    def test_get_currency_from_rate_card_with_empty_json(self):
        rate_card_json_data = None
        policy_type = "Compute"
        unit_of_measure = "USD"
        self.assertRaises(Exception('Empty Rate Card..'),
                          self.cost_client.get_currency_from_rate_card(rate_card_json_data, policy_type, unit_of_measure))

    def test_get_unit_cost_from_rate_card(self):
        rate_card_json_data = [
            {
                "policy_type": "Compute",
                "name": "broker_egl@vsphere.local",
                "unit_of_measure": "Per vCPU",
                "unit_cost": 0.5,
                "currency": "USD"
            },
            {
                "policy_type": "Compute",
                "name": "broker_egl@vsphere.local",
                "unit_of_measure": "Per GB",
                "unit_cost": 0.5,
                "currency": "USD"
            },
            {
                "policy_type": "Storage",
                "name": "broker_egl@vsphere.local",
                "unit_of_measure": "Per GB",
                "unit_cost": 0.5,
                "currency": "USD"
            }
        ]
        policy_type = "Compute"
        unit_of_measure = "Per vCPU"
        self.cost_client.get_unit_cost_from_rate_card(rate_card_json_data, policy_type, unit_of_measure)

    def test_get_unit_cost_from_rate_card_with_empty_json(self):
        rate_card_json_data = None
        policy_type = "Compute"
        unit_of_measure = "USD"
        self.assertRaises(Exception('Empty Rate Card..'),
                          self.cost_client.get_unit_cost_from_rate_card(rate_card_json_data, policy_type,
                                                                        unit_of_measure))

    @mock.patch('requests.get', side_effect=mock_client.MockCost.mocked_requests_get)
    def test_connect_vmware(self, mock_request):
        url = 'https://localhost:8080/identity/api/tokens'
        headers = {}
        isjson_resp = 'false'
        self.cost_client.connect_vmware(url, headers, isjson_resp)

    @mock.patch('requests.get', side_effect=mock_client.MockCost.mocked_requests_get)
    def test_connect_vmware1(self, mock_request):
        url = 'https://localhost:8080/identity/api/tokens'
        headers = {}
        isjson_resp = 'true'
        self.cost_client.connect_vmware(url, headers, isjson_resp)

    @mock.patch('requests.get', side_effect=mock_client.MockCost.mocked_requests_get1)
    def test_connect_vmware2(self, mock_request):
        url = 'https://localhost:8080/identity/api/tokens'
        headers = {}
        isjson_resp = 'true'
        self.cost_client.connect_vmware(url, headers, isjson_resp)


if __name__ == '__main__':
    unittest.main()