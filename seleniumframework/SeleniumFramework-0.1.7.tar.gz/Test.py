import sys
import json
from BaseTest import BaseTest
import os
import unittest


class Test:

    suite_data = object
    base_path = ''
    result = {}

    def load_data(self, json_file: str):
        with open(json_file) as json_data:
            json_text = json_data.read()
            return json.loads(json_text)

    def run_test_from_file(self, json_file, verbose=1):

        self.suite_data = self.load_data(json_file)

        test_suite = unittest.TestSuite()

        self.result["tests"] = []

        result = False

        try:
            test_suite.addTest(
                BaseTest(
                    "run_test",
                    self.base_path + json_file,
                    self.suite_data,
                    self.base_path,
                    self.result["tests"]
                )
            )

            unittest.TextTestRunner(verbosity=2).run(test_suite)

            result = True
        except Exception as e:
            self.result["message"] = "{0}".format(e)
        finally:
            self.result["result"] = str(result).lower()

        # self.result["end"] = "acabo a las 5:60"

        if verbose == 1:
            print(json.dumps(self.result))


if __name__ == "__main__":
    Test().run_test_from_file(sys.argv[1], int(sys.argv[2]))

