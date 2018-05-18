import unittest
import renderer.settings as stg
import renderer.examples.data as dt
from iohandler import IOFile
from renderer.bridge_context import Context


class UnicodifierTest(unittest.TestCase):
    def __init__(self, methodname='runTest'):
        super(UnicodifierTest, self).__init__(methodname)
        self._file_handler = IOFile.IOFileHandler()
        self._context = Context()

    def test_standalone_list(self):
        with self._file_handler.open(file_name='locale.json',
                                     file_path=stg.tests_path,
                                     create_file_if_none=False,
                                     create_package=False, mode='rb') as json_io:
            result = self._context.render(self._file_handler.read(json_io), target='file')
        with self._file_handler.open(file_name='test_standalone_list.tlog', file_path=stg.logs_path,
                                     create_file_if_none=True, create_package=False,
                                     mode='ab+') as list_to_file:
            w = self._file_handler.write(file_object=list_to_file, data=result)
        self.assertIsInstance(w, bool)
        pass

    def test_standalone_string(self):
        result = self._context.render(dt.urdu_text, target='code')
        with self._file_handler.open(file_name='test_standalone_string.tlog',
                                     file_path=stg.logs_path, create_file_if_none=True,
                                     create_package=False, mode='ab+') as string_to_file:
            w = self._file_handler.write(file_object=string_to_file, data=result)
        self.assertIsInstance(w, bool)
        pass

    def test_standalone_json_write(self):
        with self._file_handler.open(file_name='test.json', file_path=stg.tests_path,
                                     create_file_if_none=False, create_package=False, mode='rb') \
                as test_io:
            result = self._context.render(self._file_handler.read(test_io), target='file')
        with self._file_handler.open(file_name='test_standalone_json.tlog',
                                     file_path=stg.logs_path, create_file_if_none=True,
                                     create_package=False, mode='ab+') as target_file_object:
            w = self._file_handler.write(file_object=target_file_object, data=result)
        self.assertIsInstance(w, bool)
        pass


if __name__ == '__main__':
    unittest.main()
