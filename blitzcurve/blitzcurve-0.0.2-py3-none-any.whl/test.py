import blitzcurve
import os
from os import path
from shutil import copyfile

def run_test(test_dir):
    """Tests blitzcurve run_fit and run_compare on the user's system.

    Parameters
    ----------
    test_dir : str
        Test directory, where output files will be saved

    Usage
    -------
    import blitzcurve
    test_dir = r"D:\data\test"
    blitzcurve.run_test(test_dir)
    """
    name_dict = {"example_data_01.txt": "test1", "example_data_02.txt": "test2"}

    blitzcurve_module_dir = path.dirname(path.abspath(blitzcurve.__file__))
    example_dir = path.join(blitzcurve_module_dir, "examples")
    files = ["example_data_01.txt", "example_data_02.txt"]
    #files = [path.join(example_dir, "example_data_01.txt"), path.join(example_dir, "example_data_01.txt")]

    # create test path and copy data files from module to path
    if not path.isdir(test_dir):
        os.makedirs(test_dir)
    for filename in files:
        copyfile(path.join(example_dir, filename), path.join(test_dir, filename))

    data_dir = test_dir
    blitzcurve.run_fit(data_dir)
    blitzcurve.run_compare(data_dir, name_dict=name_dict)
    #blitzcurve.run_compare(data_dir)