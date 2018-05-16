import unittest
import vmware.extract.utils as utils
from path import Path
import zipfile
import mock
import json


def simply_throw_exception():
    raise Exception

@unittest.skip("convert to vmware tests")
class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.pwd = Path.getcwd()
        self.workdir = self.pwd / 'test'
        self.tempdir = self.workdir / 'tmp'
        self.envextdir = self.workdir / 'ext'
        self._type = 'asset'
        self.billing_account_number = '00000'
        self.asset_account_number = 'a0000'
        self._status = 'status'
        self._period = 201709
        self._response_code = 200
        self._response = 'passed'
        self.filepath = 'path'


    def tearDown(self):
        pass

    def test_reply_body(self):
        body = utils.reply_body(self._type, self.billing_account_number, self.asset_account_number, self._status,
                                self._period, self._response_code, self._response, self.filepath)
        j_body = json.loads(body)
        self.assertEquals(j_body['type'], self._type)
        self.assertEquals(j_body['status'], self._status)


    @mock.patch('zipfile.ZipFile',side_effect=simply_throw_exception)
    def test_write_to_zipfile(self,zipfile_mock):
        try:
            utils.write_to_zipfile("test_zip",self.workdir,self.tempdir,None)
        except:
            self.fail("Exception was not caught")

    @mock.patch('zipfile.ZipFile', side_effect=simply_throw_exception)
    def test_write_to_account_zipFile(self, zipfile_mock):
        try:
            utils.write_to_account_zipfile("test_zip",None,None, self.workdir, self.tempdir, None)
        except:
            self.fail("Exception was not caught")

    @mock.patch('zipfile.ZipFile', side_effect=simply_throw_exception)
    def test_compress(self, zipfile_mock):
        try:
            utils.compress("test.zip", self.workdir)
        except:
            self.fail("Exception was not caught")



if __name__ == '__main__':
    unittest.main()