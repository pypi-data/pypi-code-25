import os
from click.testing import CliRunner

from sblu.cli.measure import cmd_ftrmsd

from .. import DATA_DIR


def test_pwrmsd():
    runner = CliRunner()

    with runner.isolated_filesystem():
        pdb_file = DATA_DIR / 'pdb' / '1ck7.clean.pdb'
        ft_file = DATA_DIR / 'ft' / 'ft.test'
        rot_prm = DATA_DIR / 'prms' / 'rotation_test_set.mol2'

        result = runner.invoke(cmd_ftrmsd.cli, [pdb_file, pdb_file, ft_file, rot_prm,
                                                "-o", "rmsds.txt"])

        # Just a basic sanity check that ftrmsd doesn't crash and produces an output file
        # TODO: tests for correctness
        assert result.exit_code == 0
        assert os.path.exists('rmsds.txt')
