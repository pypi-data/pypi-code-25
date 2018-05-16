import unittest
import mock
from vmware.extract.process import Client
from path import Path
import logging
from vmware.extract.log import configure_logging
from vmware.extract import utils
import pika
from vmware.extract import  command_process as cp
import json


def mock_ch_basic_publish_exception():
    raise Exception("Connection was closed")

class Test_Process(unittest.TestCase):

    def setUp(self):
        self._workdir = Path.getcwd()
        self.process_client = Client(self._workdir)

    def tearDown(self):
        self.process_client = None

    @unittest.skip('skipping due to logger')
    @mock.patch('vmware.extract.utils.create_connection',
                side_effect=mock.MagicMock)
    def test_public_progress(self, mocked_connection):
        message = "test message"
        self.process_client.publish_progress(message, "channel", "properties")

    @mock.patch('pika.channel.Channel.basic_publish',
                side_effect=mock_ch_basic_publish_exception)
    @mock.patch('vmware.extract.utils.create_connection',
                side_effect=mock.MagicMock)
    def test_publish_message(self, mocked_connection, mocked_basic_publish, ):
        with self.assertRaises(Exception):
            self.process_client.publish_message("Test Message")

if __name__=="__main__":
    unittest.main()
