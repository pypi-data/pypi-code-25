"""This module contains a helper function to unpack a zip file
created by the ``base_sys_script`` into the right location and
format
"""


import shutil
import os
import zipfile


def unpack(packed_zip):
    """Unpack a zip file prepared by base_sys_script

    This function unpacks the zip file, removes the env.yml and
    min-deps.json files from it and repacks the remaining files
    back as pkg.zip for use with the migrator

    Args:
        :packed_zip (str): Absolute path to the zip file
    """
    dirname = os.path.basename(packed_zip).split('.')[0]
    os.mkdir(dirname)
    os.chdir(dirname)

    zfile = zipfile.ZipFile(packed_zip)
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        if filename == '':
            if not os.path.isdir(dirname):
                os.mkdir(dirname)
        else:
            with open(name, 'wb') as f_obj:
                f_obj.write(zfile.read(name))
    zfile.close()

    app_zip_file = zipfile.ZipFile('pkg.zip', 'w')
    app_zip_file.write(dirname)
    for pardir, _, files in os.walk(dirname):
        for filename in files:
            app_zip_file.write(os.path.join(pardir, filename))
    app_zip_file.close()
    shutil.rmtree(dirname)
