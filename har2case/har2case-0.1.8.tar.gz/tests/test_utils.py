import json
import os
import unittest

from har2case import utils


class TestUtils(unittest.TestCase):

    @staticmethod
    def create_har_file(file_name, content):
        file_path = os.path.join(
            os.path.dirname(__file__), "data", "{}.har".format(file_name))
        with open(file_path, "w") as f:
            f.write(json.dumps(content))

        return file_path

    @classmethod
    def setUpClass(cls):
        cls.har_path = os.path.join(
            os.path.dirname(__file__), "data", "demo.har")
        cls.empty_file_path = TestUtils.create_har_file(file_name="empty", content="")
        cls.empty_json_file_path = TestUtils.create_har_file(file_name="empty_json", content={})

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.empty_file_path)
        os.remove(cls.empty_json_file_path)

    def test_load_har_log_entries(self):
        log_entries = utils.load_har_log_entries(self.har_path)
        self.assertIsInstance(log_entries, list)
        self.assertIn("request", log_entries[0])
        self.assertIn("response", log_entries[0])

    def test_load_har_log_key_error(self):
        with self.assertRaises(SystemExit):
            utils.load_har_log_entries(self.empty_json_file_path)

    def test_load_har_log_empty_error(self):
        with self.assertRaises(SystemExit):
            utils.load_har_log_entries(self.empty_file_path)

    # def test_x_www_form_urlencoded(self):
    #     origin_dict = {"a":1, "b": "2"}
    #     self.assertIn("a=1", utils.x_www_form_urlencoded(origin_dict))
    #     self.assertIn("b=2", utils.x_www_form_urlencoded(origin_dict))

    def test_convert_list_to_dict(self):
        origin_list = [
            {"name": "v", "value": "1"},
            {"name": "w", "value": "2"}
        ]
        self.assertEqual(
            utils.convert_list_to_dict(origin_list),
            {"v": "1", "w": "2"}
        )
