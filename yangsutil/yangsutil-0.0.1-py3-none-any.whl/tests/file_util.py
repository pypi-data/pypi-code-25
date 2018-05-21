import os
import shutil
import unittest

from yangsutil import FileUtil


class FileUtilTestCase(unittest.TestCase):
    def setUp(self):
        self.DIRECTORY = 'log/test'
        self.FILE_NAME = 'test.log'
        self.CONTENTS = 'I Love Jellicle'

        self.META_DIRECTORY = 'tests/meta_file'

    def test_1_file_read_write(self):
        file_path = os.path.join(self.DIRECTORY, self.FILE_NAME)

        FileUtil.save_file(
            file_path=file_path,
            string_contents=self.CONTENTS
        )

        self.assertTrue(
            os.path.isfile(file_path),
            msg='file generate'
        )

        self.assertEqual(
            FileUtil.read_file(file_path),
            'I Love Jellicle',
            msg='file read'
        )

    def test_2_json_read_write(self):
        file_path = os.path.join(self.DIRECTORY, 'test.json')

        self.assertIsNone(
            FileUtil.read_json_file(file_path),
            msg='json file return None'
        )

        FileUtil.save_json_file(
            file_path=file_path,
            dict_contents={'a': 'b'}
        )
        self.assertDictEqual(
            FileUtil.read_json_file(file_path),
            {'a': 'b'},
            msg='json file contents'
        )

    def test_3_save_csv_file(self):
        file_path = os.path.join(self.DIRECTORY, 'test.csv')

        self.assertTrue(
            FileUtil.save_csv_file(
                file_path=file_path,
                dict_list=[
                    {'a': 1, 'b': 'asdf'},
                    {'a': 2, 'b': 'qwer'},
                ])
        )

    def tearDown(self):
        if os.path.isdir(self.DIRECTORY) is True:
            shutil.rmtree(self.DIRECTORY)
