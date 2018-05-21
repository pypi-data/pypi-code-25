import logging
import os
import shutil
import unittest
from datetime import datetime

from yangsutil import LogUtil
from yangsutil import log_util


class LogUtilTestCase(unittest.TestCase):
    def setUp(self):
        self.APP_NAME = '   I Love Jellicle    '

    def test_1_log_file(self):
        self.assertEqual(
            LogUtil.log_dir(app_name=self.APP_NAME),
            'log/I_Love_Jellicle',
            msg='Directory Verify'
        )

        self.assertEqual(
            LogUtil.log_file(),
            datetime.now().strftime('%Y-%m-%d.log'),
            msg='File Name Verify'
        )

    def test_2_logger(self):
        logger = LogUtil.get_logger(app_name=self.APP_NAME)

        self.assertIn(
            logger.level,
            [logging.DEBUG, logging.INFO],
            msg='Log Level'
        )
        self.assertEqual(
            logger.name,
            'yangs_util',
            msg='Log Name Verify'
        )

    def test_5_log_file_exist(self):
        LogUtil.get_logger(app_name=self.APP_NAME)

        file_path = os.path.join(
            LogUtil.log_dir(app_name=self.APP_NAME),
            LogUtil.log_file()
        )

        self.assertTrue(
            os.path.isfile(file_path),
            msg='is exist log file'
        )

    def tearDown(self):
        shutil.rmtree(log_util.LOG_ROOT)
