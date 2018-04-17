import unittest
import unittest.mock as mock

from pynucamino import Nucamino


class TestProfiles(unittest.TestCase):

    expected_profiles = ["A", "B", "C", "D", "E", "F", "G"]
    mock_output = "\n".join(expected_profiles)

    def setUp(self):
        self.decode_mock = mock.Mock(return_value=self.mock_output)
        self.stdout_mock = mock.Mock()
        self.stdout_mock.decode = self.decode_mock
        self.proc_mock = mock.Mock()
        self.proc_mock.stdout = self.stdout_mock
        self.proc_mock.check_returncode = mock.Mock(return_value=None)

    def test_profiles(self):
        with mock.patch("subprocess.run", return_value=self.proc_mock):
            Nucamino.profiles.cache_clear()
            profiles = Nucamino.profiles()
            self.assertEqual(profiles, self.expected_profiles)
            self.proc_mock.check_returncode.assert_called()
            self.proc_mock.stdout.decode.assert_called_with("utf8")

    def test_profiles_cache(self):
        with mock.patch("subprocess.run", return_value=self.proc_mock) as rm:
            Nucamino.profiles.cache_clear()
            Nucamino.profiles()
            Nucamino.profiles()
            rm.assert_called_once()
            self.proc_mock.check_returncode.assert_called_once()
            self.proc_mock.stdout.decode.assert_called_once()


class TestProfileGenes(unittest.TestCase):

    expected_genes = ["LEVI", "TH", "AF", "GAP"]
    mock_profile = "pun"
    mock_output = "\n".join(expected_genes)

    def setUp(self):
        self.decode_mock = mock.Mock(return_value=self.mock_output)
        self.stdout_mock = mock.Mock()
        self.stdout_mock.decode = self.decode_mock
        self.proc_mock = mock.Mock()
        self.proc_mock.stdout = self.stdout_mock
        self.proc_mock.check_returncode = mock.Mock(return_value=None)

    @mock.patch("pynucamino.Nucamino._check_profile", return_code=None)
    def test_profile_genes(self, _check_profile):
        with mock.patch("subprocess.run", return_value=self.proc_mock):
            Nucamino.profile_genes.cache_clear()
            genes = Nucamino.profile_genes(self.mock_profile)
            self.assertEqual(genes, self.expected_genes)
            self.proc_mock.check_returncode.assert_called()
            self.proc_mock.stdout.decode.assert_called_with("utf8")
            _check_profile.assert_called_with(self.mock_profile)

    @mock.patch("pynucamino.Nucamino._check_profile", return_code=None)
    def test_profile_genes_cache(self, _check_profile):
        with mock.patch("subprocess.run", return_value=self.proc_mock):
            Nucamino.profile_genes.cache_clear()
            Nucamino.profile_genes("pun")
            Nucamino.profile_genes("pun")
            self.proc_mock.check_returncode.assert_called_once()
            self.proc_mock.stdout.decode.assert_called_once()
            _check_profile.assert_called_once_with(self.mock_profile)
