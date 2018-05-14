import unittest
import os
import os.path
import re
import sys
import tempfile
import json

from kogu import Kogu, KoguException
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import io
class KoguTests(unittest.TestCase):

    def setUp(self):
        Kogu.verbose = True

    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__
        # clear away any previous parameters.json
        self._parameters_file_name()

    def _error_names(self, missing=True):
        invalid = ["_a4", "1a", "!a", "b$b", ":F", ",",
                   "'", "1", "0.5", "-", "A B", "A-", 1, 0.5]
        empty = ["", " ", None]
        if missing:
            invalid.extend(empty)
        return invalid

    def _clean(self, s):
        s.truncate(0)
        s.seek(0)

    def _assert_warn(self, value, msg=None):
        self._assert_line_format("Warning! Kogu", value, msg)

    def _assert_line_format(self, linestart, value, msg=None):
        regex = r"^" + re.escape(linestart) + r": .*\n$"
        self.assertRegexpMatches(value, regex, msg)

    def test_comment(self):
        sys.stdout = stdout = StringIO()
        Kogu.comment("This is comment")
        k = json.loads(stdout.getvalue())
        self.assertEquals("This is comment", k["comment"])
        self._clean(stdout)

    def test_comment_linebreaks(self):
        sys.stdout = stdout = StringIO()
        Kogu.comment("This\r\nis\ncomment\r")
        k = json.loads(stdout.getvalue())
        self.assertEquals("This is comment", k["comment"])
        self._clean(stdout)

    def test_comment_empty(self):
        sys.stdout = stdout = StringIO()
        Kogu.comment("")
        self._assert_warn(stdout.getvalue())
        self._clean(stdout)

    def test_comment_numeric(self):
        sys.stdout = stdout = StringIO()
        Kogu.comment(123)
        k = json.loads(stdout.getvalue())
        self.assertEquals("123", k["comment"])        
        self._clean(stdout)

    def test_name(self):
        sys.stdout = stdout = StringIO()
        name = "nEw (nAme)!"
        Kogu.name(name)
        k = json.loads(stdout.getvalue())
        self.assertEquals(name, k["name"])
        self._clean(stdout)

    def test_name_empty(self):
        sys.stdout = stdout = StringIO()
        Kogu.name("")
        self._assert_warn(stdout.getvalue())
        self._clean(stdout)

    def test_tag(self):
        sys.stdout = stdout = StringIO()
        tag = "nEw (tAg)!"
        Kogu.tag(tag)
        k = json.loads(stdout.getvalue())
        self.assertEquals(tag, k["tag"])
        self._clean(stdout)

    def test_tag_empty(self):
        sys.stdout = stdout = StringIO()
        Kogu.tag("")
        self._assert_warn(stdout.getvalue())
        self._clean(stdout)

    def test_untag(self):
        sys.stdout = stdout = StringIO()
        tag = "nEw (tAg)!"
        Kogu.untag(tag)
        k = json.loads(stdout.getvalue())
        self.assertEquals(tag, k["untag"])
        self._clean(stdout)

    def test_untag_empty(self):
        sys.stdout = stdout = StringIO()
        Kogu.untag("")
        self._assert_warn(stdout.getvalue())
        self._clean(stdout)

    def test_plot_series_string(self):
        sys.stdout = stdout = StringIO()
        Kogu.plot("line", "x")
        k = json.loads(stdout.getvalue())
        self.assertEquals("line", k["plot"]["type"])
        self.assertIn("x", k["plot"]["metrics"])
        self._clean(stdout)

    def test_plot_series_array(self):
        sys.stdout = stdout = StringIO()
        Kogu.plot("line", ["x", "y"])
        k = json.loads(stdout.getvalue())
        self.assertIn("x", k["plot"]["metrics"])
        self.assertIn("y", k["plot"]["metrics"])
        self._clean(stdout)

    def test_plot_series_array_single(self):
        sys.stdout = stdout = StringIO()
        Kogu.plot("line", ["x"])
        k = json.loads(stdout.getvalue())
        self.assertIn("x", k["plot"]["metrics"])
        self._clean(stdout)

    def test_plot_series_array_duplicates(self):
        sys.stdout = stdout = StringIO()
        Kogu.plot("line", ["x", "x"])
        k = json.loads(stdout.getvalue())
        self.assertIn("x", k["plot"]["metrics"])
        self.assertEquals(1, len(k["plot"]["metrics"]))
        self._clean(stdout)

    def test_plot_series_set(self):
        sys.stdout = stdout = StringIO()
        Kogu.plot("line", set(["x", "x", "y"]))
        k = json.loads(stdout.getvalue())
        self.assertIn("x", k["plot"]["metrics"])
        self.assertEquals(2, len(k["plot"]["metrics"]))
        self._clean(stdout)

    def test_plot_series_invalid(self):
        sys.stdout = stdout = StringIO()
        for name in self._error_names(missing=False): # allow empty metrics in this case
            Kogu.plot("line", name)
            self._assert_warn(
                stdout.getvalue(), "Metric '%s' should not be allowed" % name)
            self._clean(stdout)

    def test_plot_options(self):
        sys.stdout = stdout = StringIO()
        Kogu.plot("line", ['test'], "Test Plot", "Y-label")
        k = json.loads(stdout.getvalue())
        self.assertEquals("line", k["plot"]["type"])
        self.assertEquals("Y-label", k["plot"]["y_label"])
        self.assertEquals("Test Plot", k["plot"]["name"])
        self.assertIn("test", k["plot"]["metrics"])
        self._clean(stdout)

    def test_plot_options_default(self):
        sys.stdout = stdout = StringIO()
        Kogu.plot("line", "test")
        k = json.loads(stdout.getvalue())
        self.assertEquals("line", k["plot"]["type"])
        self.assertEquals("Y", k["plot"]["y_label"])
        self.assertEquals("line", k["plot"]["name"])
        self.assertIn("test", k["plot"]["metrics"])        
        self._clean(stdout)

    def test_plot_options_empty(self):
        sys.stdout = stdout = StringIO()
        Kogu.plot("", "")
        self._assert_warn(stdout.getvalue())
        self._clean(stdout)

    def test_plot_options_double_quotes(self):
        sys.stdout = stdout = StringIO()
        Kogu.plot("line", ['test'], "Test 'Plot")
        k = json.loads(stdout.getvalue())
        self.assertEquals("Test 'Plot", k["plot"]["name"])
        self.assertIn("test", k["plot"]["metrics"])
        self._clean(stdout)

    def test_upload(self):
        sys.stdout = stdout = StringIO()
        with tempfile.NamedTemporaryFile() as fp:
            Kogu.upload(fp.name)
            k = json.loads(stdout.getvalue())
            self.assertEquals(fp.name, k["upload"])
        self._clean(stdout)

    def test_upload_non_existing(self):
        sys.stdout = stdout = StringIO()
        path = "/non/existing/file"
        Kogu.upload(path)
        k = json.loads(stdout.getvalue())
        self.assertEquals(path, k["upload"])        
        self._clean(stdout)

    def test_upload_empty(self):
        sys.stdout = stdout = StringIO()
        Kogu.upload("")
        self._assert_warn(stdout.getvalue(), "parameters not passed")
        self._clean(stdout)    

    def test_metrics_none(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics(None)
        self._assert_warn(stdout.getvalue(), "None is not a valid metrics dictionary")
        self._clean(stdout)

    def test_metrics_empty(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({})
        self.assertFalse(stdout.getvalue(), "Got->["+stdout.getvalue()+"] but expected empty string")
        self._clean(stdout)

    def test_metrics_none_key_and_value(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({None: None})
        self._assert_warn(stdout.getvalue(), "None is not valid key value")
        self._clean(stdout)

    def test_metrics_none_key(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({None: 3})
        self._assert_warn(stdout.getvalue(), "None is not valid key value")
        self._clean(stdout)

    def test_metrics_none_iteration(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({"x": 3}, None)
        self._assert_warn(stdout.getvalue(), "None is not a valid iteration value")
        self._clean(stdout)

    def test_metrics_string_iteration(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({"x": 3}, "string")
        self._assert_warn(stdout.getvalue(), "a string is not a valid iteration value")
        self._clean(stdout)

    def test_metrics_float_iteration(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({"x": 3}, 3.14)
        self._assert_warn(stdout.getvalue(), "a floating point number is not a valid iteration value")
        self._clean(stdout)

    def test_metrics_empty_object_iteration(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({"x": 3}, {})
        self._assert_warn(stdout.getvalue(), "a dictionary is not a valid iteration value")
        self._clean(stdout)

    def test_metrics_invalid_key(self):
        sys.stdout = stdout = StringIO()
        for name in self._error_names():
            Kogu.metrics({name: "3"})
            self._assert_warn(stdout.getvalue(), "Processing '%s' ->" % name)
            self._clean(stdout)

    def test_metrics_iteration(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({"A": "3"}, 3)
        k = json.loads(stdout.getvalue())
        self.assertEquals("3", k["metric"]["metrics"]["A"])        
        self.assertEquals(3, k["metric"]["iteration"])        
        self._clean(stdout)

    def test_metrics_iteration_default(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({"A": "3"})
        k = json.loads(stdout.getvalue())
        self.assertEquals("3", k["metric"]["metrics"]["A"])        
        self.assertEquals(-1, k["metric"]["iteration"])                
        self._clean(stdout)

    def _test_metrics_values_string(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({"A": "3", "B": "ok"})
        k = json.loads(stdout.getvalue())
        self.assertEquals("3", k["metric"]["metrics"]["A"])        
        self.assertEquals("ok", k["metric"]["metrics"]["B"])        
        self._clean(stdout)

    def _test_metrics_values_int(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({"A": 3, "B": 6})
        k = json.loads(stdout.getvalue())
        self.assertEquals(3, k["metric"]["metrics"]["A"])        
        self.assertEquals(6, k["metric"]["metrics"]["B"])        
        self._clean(stdout)

    def test_metrics_values_float(self):
        sys.stdout = stdout = StringIO()
        float_value = 1.0 / 3.0
        Kogu.metrics({"A": float_value})
        k = json.loads(stdout.getvalue())
        self.assertEquals(float_value, k["metric"]["metrics"]["A"])        
        self._clean(stdout)

    def test_metrics_values_bool(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({"b": True, "a": False})
        k = json.loads(stdout.getvalue())
        self.assertTrue(k["metric"]["metrics"]["b"])        
        self.assertFalse(k["metric"]["metrics"]["a"])        
        self._clean(stdout)

    def test_metrics_keys_strip_whitespace(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({" A ": 3})
        k = json.loads(stdout.getvalue())
        self.assertEquals(3, k["metric"]["metrics"]["A"])        
        self._clean(stdout)

    def test_metrics_keys_whitespace_duplicates(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({" B": 6, "B ": 9})
        k = json.loads(stdout.getvalue())
        self.assertEquals(9, k["metric"]["metrics"]["B"])
        self.assertNotEquals(6, k["metric"]["metrics"]["B"])    
        self._clean(stdout)

    def _test_metrics_keys_case_sensitive(self):
        sys.stdout = stdout = StringIO()
        Kogu.metrics({"b": 6, "B": 9})
        k = json.loads(stdout.getvalue())
        self.assertEquals(9, k["metric"]["metrics"]["B"])
        self.assertEquals(6, k["metric"]["metrics"]["b"])    
        self._clean(stdout)

    def test_load_parameters(self):
        params = '{"epochs":30}'

        path = os.path.join(tempfile.mkdtemp(), 'pipe')
        os.mkfifo(path)
        fd = os.open(path, os.O_RDWR|os.O_NONBLOCK)
        os.write(fd, params.encode())

        sys.stdin = stdin = io.open(fd, mode="rt")
        sys.stdout = stdout = StringIO()
        Kogu.load_parameters()

        self.assertEqual(epochs, 30)
        stdin.close()
        os.unlink(path)
        self._clean(stdout)

    def _parameters_file_name(self):
        json_path = os.path.join(sys.path[0], "parameters.json")
        try:
            os.remove(json_path)
        except OSError:
            pass
        return json_path

    def test_load_parameters_file(self):
        with open(self._parameters_file_name(), "w") as json_file:
            json_file.writelines('{"epochs":50}')
        sys.stdout = stdout = StringIO()
        Kogu.load_parameters()
        self.assertEqual(epochs, 50)
        self._clean(stdout)

    # Piped parameters overload parameters passed from
    # parameters json. Parameters available in parameters.json
    # are output via param lines
    def test_load_parameters_priority(self):       
        with open(self._parameters_file_name(), "w") as json_file:
            json_file.writelines(u'{"epochs":50,"spaces":25}')

        params = '{"epochs":10,"spaces": 22,"third":3}'

        path = os.path.join(tempfile.mkdtemp(), 'pipe')
        os.mkfifo(path)
        fd = os.open(path, os.O_RDWR|os.O_NONBLOCK)
        os.write(fd, params.encode())

        sys.stdin = stdin = io.open(fd, mode="rt")
        sys.stdout = stdout = StringIO()

        Kogu.load_parameters()

        self.assertEqual(epochs, 10)
        self.assertEqual(spaces, 22)
        self.assertEqual(third, 3)

        k = json.loads(stdout.getvalue())
        self.assertEquals(10, k["parameters"]["epochs"])
        self.assertEquals(22, k["parameters"]["spaces"])
        self.assertEquals(3, k["parameters"]["third"])

        stdin.close()
        os.unlink(path)
        self._clean(stdout)

    def test_load_parameters_file_invalid(self):
        with open(self._parameters_file_name(), "w") as json_file:
            json_file.writelines(u'epochs:55')
        sys.stdout = stdout = StringIO()
        self.assertRaises(KoguException, Kogu.load_parameters)
        self._clean(stdout)

    def test_update_parameters_values_string(self):
        sys.stdout = stdout = StringIO()
        Kogu.update_parameters({"A": "3", "B": "ok"})
        k = json.loads(stdout.getvalue())
        self.assertEquals("3", k["parameters"]["A"])
        self.assertEquals("ok", k["parameters"]["B"])
        self._clean(stdout)

    def test_update_parameters_values_int(self):
        sys.stdout = stdout = StringIO()
        Kogu.update_parameters({"A": 3, "B": 6})
        k = json.loads(stdout.getvalue())
        self.assertEquals(3, k["parameters"]["A"])
        self.assertEquals(6, k["parameters"]["B"])
        self._clean(stdout)

    def test_update_parameters_values_float(self):
        sys.stdout = stdout = StringIO()
        fl = 1.0 / 3.0
        Kogu.update_parameters({"A": fl})
        k = json.loads(stdout.getvalue())
        self.assertEquals(fl, k["parameters"]["A"])
        self._clean(stdout)

    def test_update_parameters_values_bool(self):
        sys.stdout = stdout = StringIO()
        Kogu.update_parameters({"b": True, "a": False})
        k = json.loads(stdout.getvalue())
        self.assertTrue(k["parameters"]["b"])
        self.assertFalse(k["parameters"]["a"])
        self._clean(stdout)

    def test_update_parameters_keys_strip_whitespace(self):
        sys.stdout = stdout = StringIO()
        Kogu.update_parameters({" A ": 3})
        k = json.loads(stdout.getvalue())
        self.assertEquals(3, k["parameters"]["A"])
        self._clean(stdout)

    def test_update_parameters_keys_whitespace_duplicates(self):
        sys.stdout = stdout = StringIO()
        Kogu.update_parameters({" B": 6, "B ": 9})
        k = json.loads(stdout.getvalue())
        self.assertEquals(9, k["parameters"]["B"])
        self.assertNotEquals(6, k["parameters"]["B"])
        self._clean(stdout)

    def test_update_parameters_keys_case_sensitive(self):
        sys.stdout = stdout = StringIO()
        Kogu.update_parameters({"b": 6, "B": 9})
        k = json.loads(stdout.getvalue())
        self.assertEquals(9, k["parameters"]["B"])
        self.assertEquals(6, k["parameters"]["b"])
        self._clean(stdout)

    def test_update_parameters_keys_invalid(self):
        sys.stdout = stdout = StringIO()
        for name in self._error_names():
            Kogu.update_parameters({name: "3"})
            self._assert_warn(
                stdout.getvalue(), "%s should not be valid identifier" % name)
            self._clean(stdout)

    def test_fail(self):
        sys.stdout = stdout = StringIO()
        reason = "some, reason)"
        Kogu.fail(reason)
        k = json.loads(stdout.getvalue())
        self.assertEquals(reason, k["fail"])
        self._clean(stdout)

    def test_fail_reason_empty(self):
        sys.stdout = stdout = StringIO()
        Kogu.fail()
        k = json.loads(stdout.getvalue())
        self.assertEquals("", k["fail"])
        self._clean(stdout)

if __name__ == '__main__':
    unittest.main()
