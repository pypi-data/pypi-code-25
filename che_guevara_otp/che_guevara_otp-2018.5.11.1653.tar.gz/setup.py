#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools

def main():
    setuptools.setup(
        name                 = "che_guevara_otp",
        version              = "2018.05.11.1653",
        description          = "Python OTP",
        long_description     = long_description(),
        url                  = "https://github.com/wdbm/che_guevara_otp",
        author               = "Will Breaden Madden",
        author_email         = "wbm@protonmail.ch",
        license              = "GPLv3",
        packages             = setuptools.find_packages(),
        entry_points         = {
                               "console_scripts": (
                                  "che_guevara_otp=che_guevara_otp.__init__:loop_display_TOTP_passcodes"
                               )
                               },
        include_package_data = True,
        zip_safe             = False
    )

def long_description(
    filename = "README.md"
    ):
    if os.path.isfile(os.path.expandvars(filename)):
        try:
            import pypandoc
            long_description = pypandoc.convert_file(filename, "rst")
        except ImportError:
            long_description = open(filename).read()
    else:
        long_description = ""
    return long_description

if __name__ == "__main__":
    main()
