import unittest
import mock
from vmware.extract.command_process import Client
from path import Path
import logging
from vmware.extract.log import configure_logging
from vmware.extract import utils
import pika
from vmware.extract import  command_process as cp
import json


def mock_ch_basic_publish_exception():
    raise Exception("Connection was closed")

class Test_Command_Process(unittest.TestCase):

    def setUp(self):
        self._workdir = Path.getcwd()
        self._logger =  configure_logging('vmware.extract', utils.now('%Y%m%d%H%M%S'))
        self.command_process_client = Client(self._workdir,self._logger)

    def tearDown(self):
        self.command_process_client = None

    @mock.patch('vmware.extract.utils.create_connection',
                side_effect=mock.MagicMock)
    def test_public_progress(self,mocked_connection):
        message="test message"
        self.command_process_client.publish_progress(message,"chanhe","properties")

    @mock.patch('pika.channel.Channel.basic_publish',
                side_effect=mock_ch_basic_publish_exception)
    @mock.patch('vmware.extract.utils.create_connection',
                side_effect=mock.MagicMock)
    def test_publish_message(self,mocked_connection,mocked_basic_publish,):
        with self.assertRaises(Exception):
            self.assetclient.publish_message("Test Message")

    def test__create_json_from_command(self):
        kwargs = {
            "vcenterhost":"10.154.23.150",
            "user":"broker_egl@vsphere.local",
            "password":"Brokeregl@123",
            "vrahost":"",
            "billingaccount":"default-billing-account",
            "tenant":"vsphere.local",
            "extdir":self._workdir,
        }

        json_res=cp._create_json_from_command((),**kwargs)
        json_res=json.loads(json_res)
        assert json_res['months'] == 1

    @mock.patch('pika.channel.Channel.basic_publish',
                side_effect=mock_ch_basic_publish_exception)
    def test_callback(self,mock1):
        with self.assertRaises(Exception):
            self.assetclient.publish_message("Test Message")


if __name__=="__main__":
    unittest.main()

