""" Test for RapidPeptidesGenerator.py"""
import pytest
from .context import rpg
from rpg import RapidPeptidesGenerator

def test_restricted_float(capsys):
    """Test function 'restricted_float(mc_val)'"""
    # Error test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        RapidPeptidesGenerator.restricted_float(-10)
    _, err = capsys.readouterr()
    assert err == "Value Error: miscleavage value should be between 0 and "\
                  "100.\n"
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        RapidPeptidesGenerator.restricted_float("z")
    _, err = capsys.readouterr()
    assert err == "Type Error: miscleavage value should be a float between"\
                  " 0 and 100.\n"
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    # Normal test
    assert RapidPeptidesGenerator.restricted_float(3) == 3.0

def test_restricted_enzyme_id(capsys):
    """Test function 'restricted_enzyme_id(enz_id)'"""
    # Error test
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        RapidPeptidesGenerator.restricted_enzyme_id(-10)
    _, err = capsys.readouterr()
    assert err == "Input Error: id -10 does not correspond to any enzyme. Use"\
                  " -l to get enzyme ids.\n"
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        RapidPeptidesGenerator.restricted_enzyme_id("z")
    _, err = capsys.readouterr()
    assert err == "Type Error: Enzyme id should be an integer.\n"
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    # Normal test
    assert RapidPeptidesGenerator.restricted_enzyme_id(3) == 3

def test_list_enzyme(capsys):
    """Test function 'list_enzyme()'
    This test should be run with empty user file
    """
    RapidPeptidesGenerator.list_enzyme()
    out, _ = capsys.readouterr()
    assert out == "0: Arg-C\n1: Asp-N\n2: BNPS-Skatole\n3: Caspase-1\n4: Casp"\
                  "ase-2\n5: Caspase-3\n6: Caspase-4\n7: Caspase-5\n8: Caspas"\
                  "e-6\n9: Caspase-7\n10: Caspase-8\n11: Caspase-9\n12: Caspa"\
                  "se-10\n13: Chymotrypsin-high\n14: Chymotrypsin-low\n15: Cl"\
                  "ostripain\n16: CNBr\n17: Enterokinase\n18: Factor-Xa\n19: "\
                  "Glu-C\n20: Lys-C\n21: Lys-N\n22: NTCB\n23: Pepsin-pH1.3\n2"\
                  "4: Pepsin-pH>=2\n25: Thrombin\n26: Thrombin-Sequencing-Gra"\
                  "de\n27: Trypsin\n"

def test_create_enzymes_to_use(capsys):
    """Test function 'create_enzymes_to_use(enzymes, miscleavage)'"""
    enzymes = [19, 22, 21]
    miscleavage = [1.1, 20]
    res = RapidPeptidesGenerator.create_enzymes_to_use(enzymes, miscleavage)
    assert res.__repr__() == "[Id: 19\nName: Glu-C\nRatio Miss Cleaveage: 1.1"\
                           "0%\nRules: [index=0\nletter=D\ncut=True\npos=1\n,"\
                           " index=0\nletter=E\ncut=True\npos=1\n]\n, Id: 22"\
                           "\nName: NTCB\nRatio Miss Cleaveage: 20.00%\nRules"\
                           ": [index=0\nletter=C\ncut=True\npos=0\n]\n, Id: "\
                           "21\nName: Lys-N\nRatio Miss Cleaveage: 0.00%\nRul"\
                           "es: [index=0\nletter=K\ncut=True\npos=0\n]\n]"
    enzymes = [19, 22]
    miscleavage = [1.1, 20, 40]
    res = RapidPeptidesGenerator.create_enzymes_to_use(enzymes, miscleavage)
    _, err = capsys.readouterr()
    assert err == "Warning: Too much miscleavage values. Last values will "\
                  "be ignored.\n"
    assert res.__repr__() == "[Id: 19\nName: Glu-C\nRatio Miss Cleaveage: 1.1"\
                           "0%\nRules: [index=0\nletter=D\ncut=True\npos=1\n,"\
                           " index=0\nletter=E\ncut=True\npos=1\n]\n, Id: 22"\
                           "\nName: NTCB\nRatio Miss Cleaveage: 20.00%\nRules"\
                           ": [index=0\nletter=C\ncut=True\npos=0\n]\n]"
