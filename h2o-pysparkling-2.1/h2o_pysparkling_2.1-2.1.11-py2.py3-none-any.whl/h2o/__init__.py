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

__version__ = "3.10.5.3"
__buildinfo__ = "versionFromGradle='3.10.5',projectVersion='3.10.5.3',branch='rel-vajda',lastCommitHash='4d88193fac6e2365c85e390fd24e6e0d19669916',gitDescribe='jenkins-3.10.5.2-18-g4d88193-dirty',compiledOn='2017-06-30 16:15:02',compiledBy='jenkins'"

if (__version__.endswith("99999")):
    print(__buildinfo__)

__all__ = ("connect", "init", "api", "connection", "upload_file", "lazy_import", "import_file", "import_sql_table",
           "import_sql_select", "parse_setup", "parse_raw", "assign", "deep_copy", "get_model", "get_grid", "get_frame",
           "show_progress", "no_progress", "log_and_echo", "remove", "remove_all", "rapids", "ls", "frame",
           "frames", "download_pojo", "download_csv", "download_all_logs", "save_model", "load_model", "export_file",
           "cluster_status", "cluster_info", "shutdown", "create_frame", "interaction", "as_list", "network_test",
           "set_timezone", "get_timezone", "list_timezones", "demo", "make_metrics", "cluster", "load_dataset","flow")
