import os
import filecmp
from click.testing import CliRunner
import pytest

from .. import DATA_DIR
from sblu.cli.pdb import cmd_get

with open(DATA_DIR / "pdb_list") as f:
    pdbs = [l.strip().split()[0] for l in f]

def test_get_invalid():
    runner = CliRunner()

    result = runner.invoke(cmd_get.cli, [])
    assert result.exit_code == 2


@pytest.mark.parametrize("pdb", pdbs)
def test_get(pdb):
    runner = CliRunner()

    with runner.isolated_filesystem():
        expected_pdb = DATA_DIR / 'pdb' / (pdb + '.pdb')
        out_pdb = pdb + '.pdb'

        params.append(pdb)
        result = runner.invoke(cmd_get.cli, params)

        assert result.exit_code == 0
        # Remove pesky remark lines
        assert filecmp.cmp(out_pdb, expected_pdb)
