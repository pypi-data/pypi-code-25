# -*- coding: utf-8 -*-

"""
Top-level package for ifupdown2.

.. moduleauthor:: Roopa Prabhu <roopa@cumulusnetworks.com>
.. moduleauthor:: Julien Fortin <julien@cumulusnetworks.com>

"""

__author__ = """Julien Fortin"""
__email__ = 'julien@cumulusnetworks.com'
__version__ = '1.2.0'

import os
import resource

__addon_modules_dir__ = '%s/addons/' % (os.path.dirname(os.path.realpath(__file__)))


def get_configuration_file_real_path(path_to_file):
    """
    When install via pypi or `pip install .` ifupdown2 is install in a virtualenv
    config file that should be installed in /etc/network/ifupdown2 end-up being
    installed in /usr/local/lib/python2.7/dist-packages/etc/network/ifupdown2/
    """
    if not os.path.exists(path_to_file):
        # we will try to resolve the location of our conf file
        # otherwise default to the input argument
        package_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(package_dir)
        resolved_path = '%s%s' % (parent_dir, path_to_file)

        if os.path.exists(resolved_path):
            return resolved_path

    return path_to_file


__ifupdown2_conf_path__ = get_configuration_file_real_path('/etc/network/ifupdown2/ifupdown2.conf')
__addons_conf_path__ = get_configuration_file_real_path('/etc/network/ifupdown2/addons.conf')

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

# import ifupdown2.core.config
# os.putenv('PATH', ifupdown.config.ENVPATH)
