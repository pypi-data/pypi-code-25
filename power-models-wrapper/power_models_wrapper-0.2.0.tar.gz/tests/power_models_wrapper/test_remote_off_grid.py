import unittest
from power_models_wrapper.remote_off_grid import RemoteOffGrid
import os

class TestRemoteOffGrid(unittest.TestCase):

    def test_run_model(self):

        input_data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures/files/LANL_INPUT_CORDOVA_LATEST.xlsx"))

        print("input_data_file_path: %s" % (input_data_file_path))

        remote_off_grid = RemoteOffGrid()
        result = remote_off_grid.run(input_data_file_path)

        print("result: %s)" % (result))

        #self.assertEqual(result["solver"], "Ipopt.IpoptSolver")
        #self.assertAlmostEqual(result["objective"], 5906, delta = 1)
