import filecmp
from click.testing import CliRunner

from .. import DATA_DIR
from sblu.cli.docking import cmd_gen_cluster_pdb


def test_gen_cluster_pdb():
    """
    This test is based on the docking results for the 1avx system.
    The resulting ft, rot and cluster files were doctored to reduce size,
    but cluster centers are supposed to be correct.
    """
    runner = CliRunner()

    with runner.isolated_filesystem():
        cluster_file = DATA_DIR / 'clusters.test'
        ft_file = DATA_DIR / 'ft' / 'ft.cluster_models'
        rot_prm = DATA_DIR / 'prms' / 'rot.cluster_models.mol2'
        lig_file = DATA_DIR / 'pdb' / 'cluster_models' / '1avx_l_u_nmin.pdb'

        result = runner.invoke(cmd_gen_cluster_pdb.cli, [cluster_file, ft_file, rot_prm, lig_file,
                                                         '-o', 'output', '--max-clusters', '3'])

        assert result.exit_code == 0
        # Validate output pdb files
        for i in range(3):
            expected_pdb = DATA_DIR / 'pdb' / 'cluster_models' / "lig.{:02d}.pdb".format(i)
            assert filecmp.cmp("output.{:02d}.pdb".format(i), expected_pdb)


def test_gen_cluster_pdb_json():
    runner = CliRunner()

    with runner.isolated_filesystem():
        cluster_file = DATA_DIR / 'clusters.test.json'
        ft_file = DATA_DIR / 'ft' / 'ft.cluster_models'
        rot_prm = DATA_DIR / 'prms' / 'rot.cluster_models.mol2'
        lig_file = DATA_DIR / 'pdb' / 'cluster_models' / '1avx_l_u_nmin.pdb'

        result = runner.invoke(cmd_gen_cluster_pdb.cli, [cluster_file, ft_file, rot_prm, lig_file,
                                                         '-o', 'output', '--max-clusters', '3'])

        assert result.exit_code == 0
        # Validate output pdb files
        for i in range(3):
            expected_pdb = DATA_DIR / 'pdb' / 'cluster_models' / "lig.{:02d}.pdb".format(i)
            assert filecmp.cmp("output.{:02d}.pdb".format(i), expected_pdb)


def test_gen_cluster_pdb_symmetry():
    """
    This test is based on a CAPRI case requiring constructing a pentamer
    The resulting ft, rot and cluster files were doctored to reduce size,
    but cluster centers are supposed to be correct.
    """
    runner = CliRunner()

    with runner.isolated_filesystem():
        cluster_file = DATA_DIR / 'clusters_sym.test'
        ft_file = DATA_DIR / 'ft' / 'ft.cluster_models_sym'
        rot_prm = DATA_DIR / 'prms' / 'rot.cluster_models_sym.mol2'
        lig_file = DATA_DIR / 'pdb' / 'cluster_models' / 'prot_sym.pdb'

        result = runner.invoke(cmd_gen_cluster_pdb.cli, [cluster_file, ft_file, rot_prm, lig_file,
                                                         '-o', 'output', '--max-clusters', '3',
                                                         '--symmetry', 'C5'])

        assert result.exit_code == 0
        # Validate output pdb files
        for i in range(3):
            expected_pdb = DATA_DIR / 'pdb' / 'cluster_models' / "lig_sym.{:02d}.pdb".format(i)
            assert filecmp.cmp("output.{:02d}.pdb".format(i), expected_pdb)
            for j in range(2,5):
                expected_pdb = DATA_DIR / 'pdb' / 'cluster_models' / "lig_sym.{:02d}.{:d}.pdb".format(i, j)
                assert filecmp.cmp("output.{:02d}.{:d}.pdb".format(i, j), expected_pdb)
