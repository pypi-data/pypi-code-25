#!/usr/bin/env python
import unittest

from io import StringIO
from os import chdir, getcwd
from os.path import dirname
from shutil import rmtree
from tempfile import mkdtemp
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch  # type: ignore

from terragrunt_source import main

VALID_TERRAFORM_CONFIG = """
terragrunt = {
  include {
    path = "${find_in_parent_folders()}"
  }

  terraform {
    source = "git@github.com:cites-illinois/modules.git//lambda?ref=v0.6.2"
  }
}
"""


class TerragruntSource(unittest.TestCase):
    """ Tests various SAML helper functions """

    def setUp(self):
        self.tmpdir = mkdtemp()
        self.addCleanup(rmtree, self.tmpdir)

        self.addCleanup(chdir, getcwd())
        chdir(dirname(self.tmpdir))

    def test_valid_file(self):
        """terragrunt-source returns 0 with valid input. """
        env = {'TERRAGRUNT_DEFAULT_MODULES_REPO': '/usr/src/modules'}

        with open('terraform.tfvars', 'w') as f:
            f.write(VALID_TERRAFORM_CONFIG)

        with patch('sys.stdout', new=StringIO()) as stdout:
            with patch.dict('os.environ', env):
                with self.assertRaises(SystemExit) as cm:
                    main()

        exp = cm.exception
        self.assertEqual(exp.code, 0)

        self.assertEqual(stdout.getvalue().strip(), '/usr/src/modules//lambda')


if __name__ == '__main__':
    suite = unittest.TestSuite()
    unittest.main()
