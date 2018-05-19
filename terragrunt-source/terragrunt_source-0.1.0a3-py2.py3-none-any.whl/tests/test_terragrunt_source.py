#!/usr/bin/env python
import unittest

from io import StringIO
from os import chdir, getcwd
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
        # Create temp dir
        self.tmpdir = mkdtemp()
        self.addCleanup(rmtree, self.tmpdir)

        # Change working directory to tempdir
        self.addCleanup(chdir, getcwd())
        chdir(self.tmpdir)

    def assertTerragruntSource(self, test_output, environment, code, mesg):
        with patch(test_output, new=StringIO()) as out:
            with patch.dict('os.environ', environment, clear=True):
                with self.assertRaises(SystemExit) as cm:
                    main()

        exp = cm.exception
        self.assertEqual(exp.code, code)

        self.assertEqual(out.getvalue().strip(), mesg)

    def test_valid_terraform_tfvars_file(self):
        """succeeds when terraform.tfvars is present and valid. """
        env = {'TERRAGRUNT_DEFAULT_MODULES_REPO': '/usr/src/modules'}

        with open('terraform.tfvars', 'w') as f:
            f.write(VALID_TERRAFORM_CONFIG)

        mesg = '/usr/src/modules//lambda'
        self.assertTerragruntSource('sys.stdout', env, 0, mesg)

    def test_missing_terraform_tfvars_file(self):
        """returns 2 when terraform.tfvars is missing. """
        env = {'TERRAGRUNT_DEFAULT_MODULES_REPO': '/usr/src/modules'}

        mesg = "[Errno 2] No such file or directory: 'terraform.tfvars'"
        self.assertTerragruntSource('sys.stderr', env, 2, mesg)

    def test_missing_environment_var(self):
        """returns 3 when TERRAGRUNT_DEFAULT_MODULES_REPO is unset. """
        mesg = "Environment variable TERRAGRUNT_DEFAULT_MODULES_REPO " \
               "is undefined!"

        self.assertTerragruntSource('sys.stderr', {}, 3, mesg)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    unittest.main()
