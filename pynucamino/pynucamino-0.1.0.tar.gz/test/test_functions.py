import pathlib
import unittest
from unittest import mock

import pynucamino.functions as functions


class BaseAlignmentTest(unittest.TestCase):

    mock_seq = "> Mock Sequence\ngattaca"
    mock_profile = "pun"
    mock_genes = ("ralphlauren", "hollister")
    mock_result = {"mock": "result"}

    def setUp(self):
        self.mock_alignment = mock.Mock()
        self.mock_alignment.result = self.mock_result
        super().setUp()

    def check_mock_nucamino(self, nuc_mock):
        nuc_mock.assert_called_with(
            seqs=self.mock_seq,
            profile=self.mock_profile,
            genes=self.mock_genes,
            check=True,
        )

    def patched_nucamino(self):
        target = "pynucamino.functions.Nucamino"
        return mock.patch(target, return_value=self.mock_alignment)


class TestAlign(BaseAlignmentTest):

    def test_align(self):
        with self.patched_nucamino() as nuc_mock:
            result = functions.align(
                seqs=self.mock_seq,
                profile=self.mock_profile,
                genes=self.mock_genes,
            )
            self.assertEqual(result, self.mock_result)
            self.check_mock_nucamino(nuc_mock)


class TestAlignFile(BaseAlignmentTest):

    def new_mock_file(self):
        read_mock = mock.Mock(return_value=self.mock_seq)
        close_mock = mock.Mock()
        mock_file = mock.Mock()
        mock_file.read = read_mock
        mock_file.close = close_mock
        return mock_file

    def check_mock_file(self, mock_file):
        mock_file.read.assert_called()
        mock_file.close.assert_called()

    def test_align_file_with_file(self):
        mock_file = self.new_mock_file()
        with self.patched_nucamino() as nuc_mock:
            result = functions.align_file(
                mock_file,
                profile=self.mock_profile,
                genes=self.mock_genes,
            )
            self.assertEqual(result, self.mock_result)
            self.check_mock_nucamino(nuc_mock)
        self.check_mock_file(mock_file)

    def test_align_file_with_string(self):
        mock_file = self.new_mock_file()
        mock_filename = "mock_filename.fasta"
        with mock.patch("builtins.open", return_value=mock_file) as open_mock:
            with self.patched_nucamino() as nuc_mock:
                result = functions.align_file(
                    mock_filename,
                    profile=self.mock_profile,
                    genes=self.mock_genes,
                )
                self.assertEqual(result, self.mock_result)
                self.check_mock_nucamino(nuc_mock)
            open_mock.assert_called_with(mock_filename, 'r')

    def test_align_file_with_path(self):
        mock_file = self.new_mock_file()
        mock_path = pathlib.Path("mock_filename.fasta")
        with mock.patch("builtins.open", return_value=mock_file) as open_mock:
            with self.patched_nucamino() as nuc_mock:
                result = functions.align_file(
                    mock_path,
                    profile=self.mock_profile,
                    genes=self.mock_genes,
                )
                self.assertEqual(result, self.mock_result)
                self.check_mock_nucamino(nuc_mock)
            open_mock.assert_called_with(mock_path, 'r')
