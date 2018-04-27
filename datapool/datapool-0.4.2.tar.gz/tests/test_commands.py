# encoding: utf-8
from __future__ import print_function, division, absolute_import

from functools import partial
import io
import os
import pathlib
import shutil
import sys
import threading
import time

import pytest

from datapool.errors import DataPoolIOError
from datapool.utils import find_executable, is_server_running, write_pid_file, remove_pid_file

from datapool.commands import (start_develop, check, check_config, update_operational, init_config,
                               init_db, run_simple_server, create_example, add as _add,
                               delete_signals, delete_meta)

from datapool.landing_zone import LandingZone

from .conftest import _fix_reg_output, not_for_root

has_matlab = find_executable("matlab") is not None


def add(lz, what, settings, print_ok, print_err, input_):
    print_ok("add({!r}, {!r}, {!r}, print_ok, print_err, {!s})".format(lz, what, settings,
                                                                       input_.__name__))
    _add(lz, what, settings, print_ok, print_err, input_)


@pytest.yield_fixture(scope="function")
def m_regtest(regtest):
    """
    return regest fixture with identifier based on found / missing matlab. this identifier
    is incorporated to the file name holding the recorded output.
    so we get here different such files depending on the fact of matlab is installed or not.
    """
    if has_matlab:
        regtest.identifier = "with_matlab"
    else:
        regtest.identifier = "without_matlab"
    yield regtest
    del regtest.identifier


def _print_filtered(tmpdir, file, file0, *args, **kw):
    """replaces tmpdir substrings from output which could change from test to test
    """
    stream = io.StringIO()
    if "fg" in kw:
        kw.pop("fg")
    print(*args, file=stream, **kw)
    content = _fix_reg_output(stream.getvalue())
    file.write(content)
    file0.write(content)


@pytest.fixture
def print_ok(m_regtest, tmpdir):
    """returns print_ok function which prints using m_regtest and replaces tmpdir substrings,
    adds prefix 'stdout:' to every line
    """
    return partial(_print_filtered, tmpdir, m_regtest, sys.stdout, "stdout:")


@pytest.fixture
def print_err(m_regtest, tmpdir):
    """returns print_ok function which prints using m_regtest and replaces tmpdir substrings,
    adds prefix 'stderr:' to every line
    """
    return partial(_print_filtered, tmpdir, m_regtest, sys.stdout, "stderr:")


def test_init_config(print_ok, print_err, tmpdir, monkeypatch, regtest_list_folders):

    monkeypatch.setenv("ETC", tmpdir.strpath)

    fresh_landing_zone = tmpdir.join("landing_zone").mkdir().strpath
    assert init_config(fresh_landing_zone, False, False, print_ok, print_err) == 0

    regtest_list_folders(fresh_landing_zone, recurse=True)

    # try new folder, should fail because the datapool config folder was created before:
    non_existing_folder = tmpdir.join("landing_zone_0").mkdir().strpath
    assert init_config(non_existing_folder, False, False, print_ok, print_err) == 1


def test_init_config_sqlite_db(print_ok, print_err, tmpdir, monkeypatch, regtest_list_folders):

    monkeypatch.setenv("ETC", tmpdir.strpath)

    fresh_landing_zone = tmpdir.join("landing_zone").mkdir().strpath
    assert init_config(fresh_landing_zone, False, True, print_ok, print_err) == 0


def test_init_db(print_ok, print_err, tmpdir, monkeypatch, regtest_list_folders):

    monkeypatch.setenv("ETC", tmpdir.strpath)
    from datapool.config_handling import read_config, write_config

    # without init_config:
    assert init_db(False, False, print_ok, print_err) == 1

    # we setup a config, but setup local db
    fresh_landing_zone = tmpdir.join("landing_zone").mkdir().strpath
    init_config(fresh_landing_zone, False, False, print_ok, print_err)
    config = read_config()
    config.db.connection_string = "sqlite+pysqlite:///{}/develop.db".format(tmpdir)
    write_config(config)

    print_ok("")
    print_ok("REGULAR INIT DB:")
    assert init_db(False, False, print_ok, print_err) == 0

    print_ok("")
    print_ok("INIT BUT DB EXISTS:")
    # db already exists
    assert init_db(False, False, print_ok, print_err) == 1

    # with reset:
    print_ok("")
    print_ok("INIT, DB EXISTS BUT WE USE RESET:")
    assert init_db(True, False, print_ok, print_err) == 0


def test_check_config(print_ok, print_err, tmpdir, monkeypatch, regtest_list_folders):
    from datapool.config_handling import read_config, write_config

    monkeypatch.setenv("ETC", tmpdir.strpath)
    assert check_config(print_ok, print_err) == 1

    fresh_landing_zone = tmpdir.join("landing_zone")
    fresh_landing_zone.mkdir()
    print_ok("init config:\n")
    init_config(fresh_landing_zone.strpath, False, False, print_ok, print_err)

    print_ok("\ncheck config:\n")
    assert check_config(print_ok, print_err) == 1

    config = read_config()
    config.julia.version = "0.0.0"
    write_config(config)
    print_ok("\ncheck config:\n")
    assert check_config(print_ok, print_err) == 1


def test_start_develop(print_ok, print_err, tmpdir, monkeypatch, regtest_list_folders):
    from datapool.config_handling import read_config, write_config

    monkeypatch.setenv("ETC", tmpdir.strpath)

    operational_landing_zone = tmpdir.join("landing_zone").mkdir()

    print_ok("init config:\n")
    init_config(operational_landing_zone.strpath, False, False, print_ok, print_err)

    llz = tmpdir.join("local_landing_zone")

    sd = partial(start_develop, verbose=False, print_ok=print_ok, print_err=print_err)

    print_ok("\nstart develop:\n")
    sd(llz.strpath, reset=False)

    regtest_list_folders(llz.strpath, recurse=True)

    # overwrite existing landing zone, reset = True
    print_ok("\nstart develop:\n")
    sd(llz.strpath, reset=True)

    regtest_list_folders(llz.strpath, recurse=True)

    # error case: try to overwrite existing landing zone, reset = False
    print_ok("\nstart develop:\n")

    sd(llz.strpath, reset=False)

    # fresh landing zone but develop db already holds the tables:
    config = read_config()
    config.db.connection_string = "sqlite+pysqlite:///{}/fake_master.db".format(tmpdir)
    write_config(config)
    assert init_db(False, False, print_ok, print_err) == 0

    # inject invalid operational landing zone
    config.landing_zone.folder += "x"
    write_config(config)
    assert sd(llz.strpath, reset=True) == 1


@not_for_root
def test_start_develop_no_permissions(print_ok, print_err, tmpdir, monkeypatch, regtest_list_folders):

    monkeypatch.setenv("ETC", tmpdir.strpath)

    operational_landing_zone = tmpdir.join("landing_zone").mkdir()

    print_ok("init config:\n")
    init_config(operational_landing_zone.strpath, False, False, print_ok, print_err)

    llz = tmpdir.join("local_landing_zone")
    sd = partial(start_develop, verbose=False, print_ok=print_ok, print_err=print_err)

    print_ok("\nstart develop:\n")
    sd(llz.strpath, reset=False)

    if 1:
        # wrong access rights for reset of existing landing zone:
        print_ok("\nstart develop:\n")
        llz.chmod(0o444)
        sd(llz.strpath, reset=True)
        llz.chmod(0o777)

        # wrong access rights for copying landing zone:
        operational_landing_zone.chmod(0o000)
        assert sd(llz.strpath, reset=True) == 1
        operational_landing_zone.chmod(0o777)


def test_update_operational(print_ok, print_err, tmpdir, monkeypatch, regtest, data_path):
    from datapool.config_handling import read_config

    monkeypatch.setenv("ETC", tmpdir.join("etc").strpath)

    operational_landing_zone = tmpdir.join("landing_zone").mkdir()
    llz = tmpdir.join("local_landing_zone")

    # sd = partial(start_develop, verbose=False, print_ok=print_ok, print_err=print_err)
    sd = partial(start_develop, verbose=False, print_ok=print_ok, print_err=print_err)
    ce = partial(create_example, print_ok=print_ok, print_err=print_err)
    uo = partial(update_operational, verbose=True, print_ok=print_ok, print_err=print_err,)

    init_config(operational_landing_zone.strpath, True, True, print_ok, print_err)
    config = read_config()
    init_db(reset=True, verbose=False, print_ok=print_ok, print_err=print_err)

    assert sd(llz.strpath, reset=False) == 0

    # simulate server is running:
    write_pid_file(config)

    print_ok("")
    print_ok("update_operational from empty landing zone, no write permissions".upper())
    operational_landing_zone.chmod(0o555)  # "rx"
    lz = LandingZone(llz.strpath)
    assert uo(llz.strpath, overwrite=False, copy_raw=False) == 1

    print_ok("")
    print_ok("update_operational from empty landing zone with write permissions".upper())
    operational_landing_zone.chmod(0o777)  # "rwx"
    lz = LandingZone(llz.strpath)
    assert uo(llz.strpath, overwrite=False, copy_raw=False) == 1

    assert ce(llz.strpath, reset=True) == 0

    lz = LandingZone(llz.strpath)
    lz.overwrite_file("sites/example_site/site.yaml", data_path("yamls/modified_site.yaml"))

    # can not assume that matlab is available:
    if not has_matlab:
        llz.join("data/sensor_from_company_xyz/sensor_instance_matlab").remove(rec=1)

    print_ok("")
    print_ok("regular update_operational".upper())
    assert uo(llz.strpath, overwrite=False, copy_raw=False) == 0

    print_ok("")
    print_ok("update_operational zero updates:".upper())
    uo(llz.strpath, overwrite=False, copy_raw=True)

    remove_pid_file(config)
    print_ok("")
    print_ok("update_operational without server pid file".upper())
    uo(llz.strpath, overwrite=False, copy_raw=False)


def test_check(print_ok, print_err, tmpdir, monkeypatch, data_path):

    monkeypatch.setenv("ETC", tmpdir.strpath)

    operational_landing_zone = tmpdir.join("landing_zone").mkdir()

    print_ok("init config:\n")
    init_config(operational_landing_zone.strpath, sqlite_db=True, reset=True, print_ok=print_ok,
                print_err=print_err)

    init_db(reset=True, verbose=False, print_ok=print_ok, print_err=print_err)

    llz = tmpdir.join("local_landing_zone")

    ce = partial(create_example, print_ok=print_ok, print_err=print_err)

    print_ok("")
    print_ok("START DEVELOP")
    assert ce(llz.strpath, reset=False) == 0

    # ok
    print_ok("")
    print_ok("CHECK OK")
    # remove matlab stuff recursively:
    if not has_matlab:
        llz.join("data/sensor_from_company_xyz/sensor_instance_matlab").remove(rec=1)
    check(llz.strpath, None, False, print_ok, print_err, run_twice=False)

    print_ok("")
    print_ok("CHECK SCRIPT EXISTS BUT NO RAW DATA FILE, SAME SCRIPT")

    # deactivate data file
    raw_data_folder = llz.join("data/sensor_from_company_xyz/sensor_instance_julia/raw_data")
    raw_data_folder.join("data-001.raw").rename(raw_data_folder.join("data-001.rawx"))

    check(llz.strpath, None, False, print_ok, print_err, run_twice=False)

    # undo deactivation raw data file
    raw_data_folder.join("data-001.rawx").rename(raw_data_folder.join("data-001.raw"))

    print_ok("")
    print_ok("YAML CHECK STILL OK")
    shutil.copy(data_path("yamls/modified_site.yaml"),
                llz.join("sites/example_site/site.yaml").strpath)
    check(llz.strpath, None, False, print_ok, print_err, run_twice=False)

    # multiple signals
    print_ok("")
    print_ok("FAILS BECAUSE DUPLICATE SIGNALS")
    raw_folder = llz.join("data/sensor_from_company_xyz/sensor_instance_python/raw_data")
    shutil.copy(raw_folder.join("data-001.raw").strpath, raw_folder.join("data-002.raw").strpath)
    check(llz.strpath, None, False, print_ok, print_err, run_twice=False)

    # cleanup
    os.remove(raw_folder.join("data-002.raw").strpath)

    # invalid path
    print_ok("")
    print_ok("CHECK NONEXISTING FOLDER")
    check("/tmp/def/this_folder_will_not_exist/42", None, True, print_ok, print_err,
          run_twice=False)

    lz = LandingZone(llz.strpath)
    lz.overwrite_file("data/sensor_from_company_xyz/sensor_instance_julia/conversion.jl",
                      data_path("failing_scripts", "conversion_exceeds_dimensions.jl"))

    print_ok("")
    print_ok("CHECK JULIA FAILS")
    # todo: restore julia folder
    check(llz.strpath, None, False, print_ok, print_err, run_twice=False)

    lz.overwrite_file("sites/example_site/site.yaml", data_path("yamls/empty.yaml"))
    lz.overwrite_file("sites/example_site/site.yaml",
                      data_path("yamls/site_with_invalid_pictures.yaml"))
    print_ok("")
    print_ok("CHECK YAMLS FAILD")
    check(llz.strpath, None, False, print_ok, print_err, run_twice=False)

    print_ok("")
    print_ok("FOLDERS FAIL")
    lz.remove_folder("data/sensor_from_company_xyz/sensor_instance_python/raw_data", force=True)
    check(llz.strpath, None, False, print_ok, print_err, run_twice=False)


def test_run_simple_server(print_ok, print_err, monkeypatch, tmpdir, lz, data_path):
    from datapool.config_handling import (init_config, read_config, write_config,
                                          config_for_develop_db)

    monkeypatch.setenv("ETC", tmpdir.strpath)

    config_folder, messages = init_config(lz.root_folder, overwrite=True, sqlite_db=False)
    config = read_config()
    config.db, __ = config_for_develop_db(lz.root_folder)
    write_config(config)

    started = None

    def run_for_n_seconds(n=2.5):
        nonlocal started
        if started is None:
            started = time.time()
        return time.time() < started + n

    def inject_change():
        while not is_server_running(config):
            time.sleep(.1)
        # invalid, triggers error
        lz.overwrite_file("test.yaml", data_path("yamls/empty.yaml"))
        time.sleep(.5)
        lz.overwrite_file("sites/example_site/site.yaml", data_path("yamls/empty.yaml"))
        time.sleep(.5)
        lz.overwrite_file("data/parameters.yaml", data_path("yamls/parameters_extended.yaml"))
        time.sleep(.5)

    threading.Thread(target=inject_change).start()
    run_simple_server(False, print_ok, print_err, run_for_n_seconds)
    assert not is_server_running(config)


def test_development_workflow(print_ok, print_err, tmpdir, monkeypatch, data_path, regtest):

    monkeypatch.setenv("ETC", tmpdir.strpath)

    operational_landing_zone = tmpdir.join("landing_zone").mkdir().strpath
    development_landing_zone = tmpdir.join("development_landing_zone").strpath

    steps = [
        partial(init_config, operational_landing_zone, True, True, print_ok, print_err),
        partial(check_config, print_ok, print_err),
        partial(init_db, True, False, print_ok, print_err),
        partial(create_example, development_landing_zone, False, print_ok, print_err),
        partial(check, development_landing_zone, None, False, print_ok, print_err),
        partial(update_operational, development_landing_zone, False, False, print_ok, print_err),
    ]

    expected_rcs = [0, 0, 0, 0, None]

    for step, expected_rc in zip(steps, expected_rcs):
        func_name = step.func.__name__
        print(file=regtest)
        print("run", func_name, file=regtest)
        rc = step()
        if expected_rc is not None and rc != expected_rc:
            print(file=regtest)
            print("=" * 100, file=regtest)
            print("{} returned {}".format(func_name, rc), file=regtest)
            print("=" * 100, file=regtest)
            print(file=regtest)
            break


def mock_input(message):
    field = message.split(" ", 1)[0]
    return field + "_x"


def mock_input_abort(message):
    return "."


def record_full_folder(tmpdir, regtest):
    print(file=regtest)
    for dirname, dirs, files in os.walk(tmpdir.strpath):
        dirname_rel = os.path.relpath(dirname, tmpdir.strpath)
        for file_ in files:

            print("  ", os.path.join(dirname_rel, file_), file=regtest)
            with open(os.path.join(dirname, file_)) as fh:
                for line in fh:
                    print("    |", line.rstrip(), file=regtest)


def test_add_ok(print_ok, print_err, tmpdir, regtest):

    print(">>> add ok site", file=regtest)
    add(tmpdir.strpath, "site", (), print_ok, print_err, input_=mock_input)
    record_full_folder(tmpdir, regtest)

    print(file=regtest)
    print(">>> add ok site abort", file=regtest)
    add(tmpdir.strpath, "site", ("name=abcd",), print_ok, print_err, input_=mock_input_abort)
    record_full_folder(tmpdir, regtest)

    print(file=regtest)
    print(">>> add ok source_type", file=regtest)
    add(tmpdir.strpath, "source_type", ("name=abc",), print_ok, print_err, input_=mock_input)
    record_full_folder(tmpdir, regtest)

    print(file=regtest)
    print(">>> add ok source", file=regtest)
    add(tmpdir.strpath, "source", ("source_type=abc",), print_ok, print_err, input_=mock_input)
    record_full_folder(tmpdir, regtest)

    print(file=regtest)
    print(">>> add ok parameter", file=regtest)
    add(tmpdir.strpath, "parameter", ("name=p1",), print_ok, print_err, input_=mock_input)
    add(tmpdir.strpath, "parameter", ("name=p2",), print_ok, print_err, input_=mock_input)
    record_full_folder(tmpdir, regtest)

    tmpdir.join(".start_state").open("w").close()

    check(tmpdir.strpath, None, False, print_ok, print_err)


def test_add_fail(print_ok, print_err, tmpdir, regtest):

    print(file=regtest)
    print(">>> add sitex fail", file=regtest)
    add(tmpdir.strpath, "sitex", (), print_ok, print_err, input_=mock_input)

    print(file=regtest)
    print(">>> add site fail wrong default setting", file=regtest)
    add(tmpdir.strpath, "site", ("name=abc=",), print_ok, print_err, input_=mock_input)

    print(file=regtest)
    print(">>> add site fail invalid field", file=regtest)
    add(tmpdir.strpath, "site", ("name=abc", "house=here",
                                 "domain=unknown"), print_ok, print_err, input_=mock_input)

    p = tmpdir.join("fail")
    p.mkdir()
    p.chmod(0o444)
    with pytest.raises(DataPoolIOError):
        add(p.strpath, "site", (), print_ok, print_err, input_=mock_input)

    print(">>> fail add parameter", file=regtest)
    add(tmpdir.strpath, "parameter", ("name=abc",), print_ok, print_err, input_=mock_input)
    add(tmpdir.strpath, "parameter", ("name=abcd",), print_ok, print_err, input_=mock_input)
    add(tmpdir.strpath, "parameter", ("name=abcd",), print_ok, print_err, input_=mock_input)

    print(">>> fail add site twice", file=regtest)
    add(tmpdir.strpath, "site", ("name=abc",), print_ok, print_err, input_=mock_input)
    add(tmpdir.strpath, "site", ("name=abc",), print_ok, print_err, input_=mock_input)

    print(">>> fail add sourc without existing source type", file=regtest)
    add(tmpdir.strpath, "source", ("source_type=abc",), print_ok, print_err, input_=mock_input)

    print(">>> fail add source_type twice", file=regtest)
    add(tmpdir.strpath, "source_type", ("name=abc",), print_ok, print_err, input_=mock_input)
    add(tmpdir.strpath, "source_type", ("name=abc",), print_ok, print_err, input_=mock_input)


def _setup(monkeypatch, tmpdir, lz, regtest_logger):
    from datapool.config_handling import (init_config, read_config, write_config,
                                          config_for_develop_db)

    from datapool.dispatcher import Dispatcher
    from datapool.database import setup_db

    monkeypatch.setenv("ETC", tmpdir.strpath)

    init_config(lz.root_folder, overwrite=True, sqlite_db=False)
    config = read_config()
    config.db, __ = config_for_develop_db(lz.root_folder)
    write_config(config)

    setup_db(config.db, verbose=False)

    with regtest_logger():
        d = Dispatcher(config)

        root = pathlib.Path(lz.root_folder)
        rel_paths = [str(p.relative_to(root)) for p in root.glob("**/*")]
        in_order, __ = LandingZone.separate_allowed_files(rel_paths)

        for rel_path in in_order:
            if "raw_data/" in rel_path:
                # skip script execution for julia and matlab scripts:
                if "flodar_julia" in rel_path or "flodar_matlab" in rel_path:
                    continue
            d.dispatch(rel_path)


def test_delete(print_ok, print_err, tmpdir, regtest, monkeypatch, lz, regtest_logger):
    _setup(monkeypatch, tmpdir, lz, regtest_logger)

    print(file=regtest)
    print("DELETE SOURCE TYPE", file=regtest)
    assert delete_meta(False, 10, "source_type", "FloDar", print_ok, print_err) == 1

    print(file=regtest)
    print("DELETE PARAMETER SHOW ONLY", file=regtest)
    assert delete_meta(False, 10, "parameter", "Distance", print_ok, print_err) == 1

    print(file=regtest)
    print("DELETE PARAMETER SHOW ONLY", file=regtest)
    assert delete_meta(False, 10, "parameter", "Water Level", print_ok, print_err) == 0

    print(file=regtest)
    print("DELETE PARAMETER", file=regtest)
    assert delete_meta(True, 10, "parameter", "Water Level", print_ok, print_err) == 0

    print(file=regtest)
    print("DELETE ALREADY DELETED PARAMETER", file=regtest)
    assert delete_meta(True, 10, "parameter", "Water Level", print_ok, print_err) == 1

    print(file=regtest)
    print("DELETE NON EXISTING SITE", file=regtest)
    assert delete_meta(False, 10, "site", "nonexisting_site", print_ok, print_err) == 1

    print(file=regtest)
    print("DELETE EXISTING SITE SHOW ONLY", file=regtest)
    assert delete_meta(False, 10, "site", "test_site", print_ok, print_err) == 0

    print(file=regtest)
    print("DELETE EXISTING SITE", file=regtest)
    assert delete_meta(True, 10, "site", "test_site", print_ok, print_err) == 0

    print(file=regtest)
    print("DELETE NON EXISTING SOURCE", file=regtest)
    assert delete_meta(False, 10, "source", "nonexisting_source", print_ok, print_err) == 1

    print(file=regtest)
    print("DELETE EXISTING SOURCE", file=regtest)
    assert delete_meta(True, 10, "source", "flodar_R", print_ok, print_err) == 0

    print("REMOVE SIGNALS FOR GIVEN PARAMETER", file=regtest)
    delete_signals(True, 11,  ["parameter=='Average Flow Velocity'"], print_ok, print_err)

    print(file=regtest)
    print("ASK FOR ALL SIGNALS BUT DONT DELETE", file=regtest)
    delete_signals(False, 10, [], print_ok, print_err)

    print(file=regtest)
    print("DELETE ALL SIGNALS", file=regtest)
    delete_signals(True, 10, [], print_ok, print_err)

    print(file=regtest)
    print("ASK FOR ALL SIGNALS BUT DONT DELETE", file=regtest)
    delete_signals(False, 10,  [], print_ok, print_err)

