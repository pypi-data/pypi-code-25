# encoding: utf-8
from __future__ import print_function, division, absolute_import

import os
import shutil

import pytest

from datapool.database import setup_db, dump_db
from datapool.errors import FatalError
from datapool.dispatcher import Dispatcher, log_unexpected_exceptions
from datapool.utils import find_executable
from datapool.logger import logger


def test_log_unexpected_exceptions(regtest_logger):
    @log_unexpected_exceptions
    def by_zero(a, b, c):
        return a + b / c

    with regtest_logger():
        by_zero(1, 2, 0)
        by_zero("1", 2, c=0)
        by_zero({1}, b="2", c=0)


def _run_dispatcher(config, regtest_logger, lz, paths):
    setup_db(config.db)
    with regtest_logger():
        dispatcher = Dispatcher(config, time_provider=lambda: "NOW")
        for path in paths:
            for message in dispatcher.dispatch(path):
                logger().info("message: {}".format(message))


def test_dispatcher_ok(config, regtest, regtest_logger, lz):
    paths = (
        "sites/example_site/site.yaml",
        "data/parameters.yaml",
        "data/FloDar/source_type.yaml",
        "data/FloDar/FloDar_python/source.yaml",
        "data/FloDar/FloDar_python/conversion.py",
        "data/FloDar/FloDar_python/raw_data/data-001.raw", )

    config.python.executable = find_executable("python")
    _run_dispatcher(config, regtest_logger, lz, paths)
    dump_db(config.db, file=regtest, max_rows=25)
    for path in lz.list_all_files():
        print(path, file=regtest)

    print("\nfiles backup landing zone:".upper(), file=regtest)
    root_backup = config.backup_landing_zone.folder
    for dirname, dirs, files in os.walk(root_backup):
        dirname = os.path.relpath(dirname, root_backup)
        for path in files:
            print("  ", os.path.join(dirname, path), file=regtest)


def test_dispatcher_corrupt_raw_file(config, regtest, regtest_logger, lz, tmpdir):

    setup_db(config.db)
    dev_root = config.landing_zone.folder
    test_root = config.landing_zone.folder = tmpdir.strpath
    config.python.executable = find_executable("python")

    def one_run(run_index):

        paths = (
            "sites/example_site/site.yaml",
            "sites/example_site/images/1.JPG",
            "sites/example_site/images/2.JPG",
            "sites/example_site/images/3.JPG",
            "sites/example_site/site.yaml",
            "data/parameters.yaml",
            "data/FloDar/source_type.yaml",
            "data/FloDar/FloDar_python/source.yaml",
            "data/FloDar/FloDar_python/conversion.py",
            "data/FloDar/FloDar_python/raw_data/data-001.raw", )

        for p in paths:
            target = os.path.join(test_root, p)
            target_folder = os.path.dirname(target)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            shutil.copy(os.path.join(dev_root, p), target)

        assert target.endswith(".raw"), "someone broke this test by changing 'paths' above"

        duplicate_signals_diff_values = "\t".join(["13.11.2013 10:06"] + 7 * ["999"])

        lines = open(target, encoding="latin-1").readlines()
        with open(target, "w", encoding="latin-1") as fh:
            fh.writelines(lines[0:2])
            fh.writelines(lines[1])
            if run_index == 1:
                fh.write(duplicate_signals_diff_values)

        with regtest_logger():
            dispatcher = Dispatcher(config, time_provider=lambda: "NOW")
            for path in paths:
                for message in dispatcher.dispatch(path):
                    logger().info("message: {}".format(message))

    one_run(0)
    dump_db(config.db, ["site", "parameter", "source", "source_type", "signal"],
            file=regtest, max_rows=25)

    # another run with dupicate signal with different value:
    one_run(1)
    dump_db(config.db, ["signal"], file=regtest, max_rows=25)

    print("\nlanding zone:".upper(), file=regtest)
    for path in lz.list_all_files():
        print("  ", path, file=regtest)

    print("\nfiles backup landing zone:".upper(), file=regtest)
    root_backup = config.backup_landing_zone.folder
    for dirname, dirs, files in os.walk(root_backup):
        dirname = os.path.relpath(dirname, root_backup)
        for path in files:
            print("  ", os.path.join(dirname, path), file=regtest)


def test_dispatcher_no_python(config, regtest_logger, lz):
    # we don't configure r here to trigger an error
    paths = ("data/FloDar/FloDar_python/conversion.py",
             "data/FloDar/FloDar_python/raw_data/data-001.raw")

    _run_dispatcher(config, regtest_logger, lz, paths)


def test_dispatcher_no_raw(config, regtest_logger, lz):
    lz.remove_file("data/FloDar/FloDar_python/raw_data/data-001.raw")
    paths = ("data/FloDar/FloDar_python/conversion.py", )
    _run_dispatcher(config, regtest_logger, lz, paths)


def test_dispatcher_no_script(config, regtest_logger, lz):
    lz.remove_file("data/FloDar/FloDar_python/conversion.py")
    paths = ("data/FloDar/FloDar_python/raw_data/data-001.raw", )
    _run_dispatcher(config, regtest_logger, lz, paths)


def test_dispatcher_multiple_scripts(config, regtest_logger, lz):
    lz.overwrite_file("data/FloDar/FloDar_python/conversion.jl",
                      lz.p("data/FloDar/FloDar_python/conversion.py"))
    paths = ("data/FloDar/FloDar_python/raw_data/data-001.raw", )
    _run_dispatcher(config, regtest_logger, lz, paths)


def test_dispatcher_wrong_yaml_name(config, regtest_logger, lz):
    paths = ("data/invalid_name.yaml", )
    for p in paths:
        open(lz.p(p), "w").close()
    try:
        _run_dispatcher(config, regtest_logger, lz, paths)
    finally:
        for p in paths:
            os.remove(lz.p(p))


def test_dispatcher_invalid_yaml(config, regtest_logger, data_path, lz):
    lz.overwrite_file("data/parameters.yaml", data_path("yamls/empty.yaml"))
    paths = ("data/parameters.yaml", )
    _run_dispatcher(config, regtest_logger, lz, paths)


def test_dispatcher_file_does_not_exist(config, regtest_logger, lz):
    # we don't configure r here to trigger an error
    paths = ("new_file.txt,")
    with pytest.raises(FatalError):
        _run_dispatcher(config, regtest_logger, lz, paths)
