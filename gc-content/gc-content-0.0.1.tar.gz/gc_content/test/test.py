import unittest
import gc_content


class TestFASTA(unittest.TestCase):
    def test_fasta(self):
        self.assertTrue(gc_content.is_fasta('poplar-primers.fa'))

if __name__ == '__main__':
    unittest.main()