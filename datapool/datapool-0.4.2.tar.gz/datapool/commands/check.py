import contextlib
import os
import shutil
import tempfile
import time

from os.path import exists, join

from ..config_handling import read_config, config_for_develop_db
from ..data_conversion import ConversionRunner
from ..database import setup_db, check_if_tables_exist, copy_db, connect_to_db
from ..domain_objects_checker import DomainObjectsChecker
from ..errors import InvalidLandingZone, DataPoolException, InvalidOperationError
from ..landing_zone import LandingZone
from ..landing_zone_structure import source_yaml_path_for_script, required_folders
from ..logger import get_cmdline_logger
from ..signal_model import check_signals_uniqueness, check_signals_against_db, check_fields
from ..uniform_file_format import to_signals
from ..utils import enumerate_filename, print_signals
from ..yaml_parsers import parse_source


def _setup(print_err, landing_zone, **kw):

    config = read_config(**kw)
    if config is None:
        print_err("- no config file found. please run 'pool init-config' first.")
        return None, None

    if not exists(landing_zone):
        print_err("  - folder {} does not exist".format(landing_zone))
        return None, None
    try:
        lz = LandingZone(landing_zone)
    except InvalidLandingZone as e:
        print_err("  - landing zone at {} invalid. reason: {}".format(landing_zone, e))
        return None, None
    return config, lz


def check(landing_zone, result_folder, verbose, print_ok, print_err, run_twice=True):

    config, lz = _setup(print_err, landing_zone)
    if config is None or lz is None:
        return 1

    print_ok("- check names and places of changed files at landing zone {}".format(landing_zone))
    all_changed_files = set(lz.list_new_and_changed_files())
    __, unknown_files = lz.separate_allowed_files(all_changed_files)

    if not unknown_files:
        print_ok("- file names and their places are ok")
    else:
        for unknown_file in unknown_files:
            print_err("- do not know how to handle file at {}".format(unknown_file))

    print_ok("- check yaml files in landing zone at {}".format(landing_zone))

    with get_cmdline_logger(verbose):
        with _setup_test_db(landing_zone, config, verbose, print_ok, print_err) as engine:

            ok = _run_folder_checks(lz, print_ok, print_err)
            if not ok:
                print_err("+ folder structure is corrupted")
                return 1

            ok = _run_yaml_checks(lz, engine, print_ok, print_err, verbose)
            if not ok:
                print_err("+ detected problems in yaml files")
                return 1
            print_ok("- all yaml files checked")

            print_ok("- check scripts landing zone at {}".format(landing_zone))
            found_errors = _run_script_checks(lz, engine, config, result_folder, verbose, run_twice,
                                              print_ok, print_err)

    if found_errors:
        print_err("+ checks failed. please fix this.")
        return 1

    print_ok("- all scripts checked")
    print_ok("+ congratulations: all checks succeeded.", fg="green")
    return 0


def _run_script_checks(lz, engine, config, result_folder, verbose, run_twice, print_ok, print_err):

    runner = ConversionRunner(config)
    result_folder = _setup_result_folder(result_folder, print_ok, print_err)

    found_errors = False
    changed_files = lz.list_new_and_changed_files()

    all_signals = []

    for script_path, data_path in lz.conversion_scripts_and_data():

        if script_path not in changed_files:
            print_ok("- skip conversion of {} by {}. script is unchanged"
                     .format(data_path, script_path))
            continue

        if data_path is None:
            found_errors = True
            print_err("- conversion script changed but no raw data file for {}".format(script_path))
            continue

        print_ok("- check {} on {}".format(script_path, data_path))

        source = _load_source(lz, script_path, print_err)
        if source is None:
            found_errors = True
            continue

        ok, needed_conv, signals = _check_conversion(runner, lz, script_path, data_path, verbose,
                                                     result_folder, source, True,
                                                     print_ok, print_err)
        if signals is not None:
            all_signals.extend(signals)

        if not ok:
            found_errors = True
        else:
            print_ok("  - first conversion needed {:.0f} msec".format(needed_conv * 1000))
            if run_twice:
                ok, needed_conv, __ = _check_conversion(runner, lz, script_path, data_path,
                                                        verbose, result_folder, source, False,
                                                        print_ok, print_err)
                if not ok:
                    found_errors = True
                else:
                    print_ok("  - second conversion needed {:.0f} msec".format(needed_conv * 1000))

    if found_errors:
        return True

    print_ok("- check signals integrity")
    found_errors = _report(check_signals_uniqueness(all_signals), print_err)
    if not found_errors:
        print_ok("- check signals against db")
        found_errors = _report(check_signals_against_db(all_signals, engine), print_err)
    return found_errors


def _load_source(lz, script_path, print_err):
    source_path = source_yaml_path_for_script(script_path)

    source = None
    for result in parse_source(lz.root_folder, source_path):
        if isinstance(result, DataPoolException):
            print_err("  - parsing {}: {}".format(source_path, result))
        else:
            source = result

    return source


def _check_conversion(runner, lz, script_path, data_path, verbose, result_folder, source,
                      backup_results, print_ok, print_err):

    signals = None

    started = time.time()
    for result in runner.check_conversion(lz.p(script_path), lz.p(data_path), verbose):
        if isinstance(result, Exception):
            print_err("  - {}".format(result))
        else:
            output_file, rows = result
            signals = to_signals(rows)

    if signals is None:
        return False, 0, signals

    needed_conv = time.time() - started

    for signal_ in signals:
        signal_.source = source.name

    if backup_results:
        _backup_results(result_folder, output_file, signals, script_path, print_ok)

    has_errors = _report(check_fields(signals), print_err)
    return not has_errors, needed_conv, signals


def _report(check_iter, print_err):
    error_count = 0
    has_errors = False
    exceptions = [result for result in check_iter if isinstance(result, Exception)]
    MAX_ERR = 10
    for exception in exceptions:
        print_err("  - {}".format(exception))
        error_count += 1
        has_errors = True
        if error_count > MAX_ERR:
            print_err("  - too many errors, skipped {} errors.".format(len(exceptions) - MAX_ERR))
            break
    return has_errors


def _setup_result_folder(result_folder, print_ok, print_err):

    if not result_folder:
        result_folder = tempfile.mkdtemp()
    else:
        if os.path.exists(result_folder):
            if not os.path.isdir(result_folder):
                print_err("+ given path {} exists but is not a folder".format(result_folder))
                return 1
        else:
            os.makedirs(result_folder)
            print_ok("- created folder {}".format(result_folder))

    return result_folder


def _backup_results(result_folder, output_file, signals, script, print_ok):
    script_folder_name = os.path.basename(os.path.dirname(script))
    csv_path = join(result_folder, script_folder_name) + ".csv"
    txt_path = join(result_folder, script_folder_name) + ".txt"

    csv_path, txt_path = enumerate_filename(csv_path, txt_path)
    shutil.copy(output_file, csv_path)
    print_ok("  - wrote conversion result as csv to {}".format(csv_path))
    with open(txt_path, "w") as fh:
        print_signals(signals, file=fh)
    print_ok("  - wrote conversion result as txt to {}".format(txt_path))


@contextlib.contextmanager
def _setup_test_db(landing_zone, config, verbose, print_ok, print_err):

    config_develop_db, path = config_for_develop_db(landing_zone)

    if os.path.exists(path):
        os.unlink(path)

    ok = False
    try:
        ok = check_if_tables_exist(config.db)
    except InvalidOperationError:
        print_err("- could not connect to productive db.")
    if not ok:
        print_err("- setup fresh development db. productive does not exist or is empty.")
        setup_db(config_develop_db, verbose=verbose)

    else:
        print_ok("- copy meta data from productive db")
        for table_name in copy_db(
                config.db, config_develop_db, delete_existing=True, copy_signals=False,
                verbose=verbose):
            print_ok("  - copy table {}".format(table_name))

    engine = connect_to_db(config_develop_db)

    yield engine

    os.unlink(path)
    engine.dispose()


def _run_folder_checks(lz, print_ok, print_err):
    print_ok("- check folder structure")
    ok = True
    for folder in required_folders(lz.root_folder):
        rel_folder = os.path.relpath(folder, lz.root_folder)
        if not os.path.exists(folder):
            print_err("  - {} does not exist".format(rel_folder))
            ok = False
        elif not os.path.isdir(folder):
            rel_folder = os.path.relpath(folder, lz.root_folder)
            print_err("  - {} is not a folder".format(rel_folder))
            ok = False
        else:
            print_ok("  - {} is ok".format(rel_folder))

    return ok


def _run_yaml_checks(lz, engine, print_ok, print_err, verbose):

    new_yamls = []
    for rel_path in lz.list_all_files():
        if not rel_path.endswith(".yaml"):
            continue
        new_yamls.append(rel_path)

    if not new_yamls:
        print_ok("- no yaml files detected. skip checks.")
        return True

    print_ok("- detected {} yaml files:".format(len(new_yamls)))
    for rel_path in new_yamls:
        print_ok("  - {}".format(lz.p(rel_path)))

    print_ok("- check yaml files")
    checker = DomainObjectsChecker(lz.root_folder, new_yamls)
    ok = True
    for error in checker.check_all(engine):
        print_err("  - got error: {}".format(error))
        ok = False

    return ok
