# -*- encoding: utf-8 -*-
# Copyright: (c) 2016 H2O.ai
# License:   Apache License Version 2.0 (see LICENSE for details)
"""
:mod:`h2o` -- module for using H2O services.

(please add description).
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from h2o.h2o import (connect, init, api, connection,
                     lazy_import, upload_file, import_file, import_sql_table, import_sql_select,
                     parse_setup, parse_raw, assign, deep_copy, get_model, get_grid, get_frame,
                     show_progress, no_progress, log_and_echo, remove, remove_all, rapids,
                     ls, frame, frames, create_frame,
                     download_pojo, download_csv, download_all_logs, save_model, load_model, export_file,
                     cluster_status, cluster_info, shutdown, network_test, cluster,
                     interaction, as_list,
                     get_timezone, set_timezone, list_timezones,
                     load_dataset, demo, make_metrics,flow)
# We have substantial amount of code relying on h2o.H2OFrame to exist. Thus, we make this class available from
# root h2o module, without exporting it explicitly. In the future this import may be removed entirely, so that
# one would have to import it from h2o.frames.
from h2o.frame import H2OFrame  # NOQA

__version__ = "3.14.0.2"
__buildinfo__ = "versionFromGradle='3.14.0',projectVersion='3.14.0.2',branch='rel-weierstrass',lastCommitHash='03e64d5c87f1eb7bcad9372bb4a73c4aab4f52d9',gitDescribe='jenkins-3.14.0.1-6-g03e64d5',compiledOn='2017-08-21 22:20:05',compiledBy='jenkins'"

if (__version__.endswith("99999")):
    print(__buildinfo__)

__all__ = ("connect", "init", "api", "connection", "upload_file", "lazy_import", "import_file", "import_sql_table",
           "import_sql_select", "parse_setup", "parse_raw", "assign", "deep_copy", "get_model", "get_grid", "get_frame",
           "show_progress", "no_progress", "log_and_echo", "remove", "remove_all", "rapids", "ls", "frame",
           "frames", "download_pojo", "download_csv", "download_all_logs", "save_model", "load_model", "export_file",
           "cluster_status", "cluster_info", "shutdown", "create_frame", "interaction", "as_list", "network_test",
           "set_timezone", "get_timezone", "list_timezones", "demo", "make_metrics", "cluster", "load_dataset","flow")
