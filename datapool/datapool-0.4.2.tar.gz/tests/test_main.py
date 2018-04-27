# encoding: utf-8
from __future__ import print_function, division, absolute_import

import os
import re
import shutil
import subprocess

from fnmatch import fnmatch

from click.testing import CliRunner

import pytest

from datapool.utils import find_executable

has_matlab = find_executable("matlab") is not None


def test_init_config(data_path, tmpdir, monkeypatch, regtest_list_folders):

    monkeypatch.setenv("ETC", tmpdir.strpath)
    from datapool.main import init_config

    runner = CliRunner()

    fresh_landing_zone = tmpdir.join("landing_zone").mkdir().strpath
    result = runner.invoke(init_config, [fresh_landing_zone])
    assert result.exit_code == 0, result.output

    regtest_list_folders(fresh_landing_zone, recurse=True)

    # try the same folder again:
    result = runner.invoke(init_config, [fresh_landing_zone])
    output = result.output.strip().split("\n")

    assert fnmatch(output[3], "*folder * already exists"), output
    assert result.exit_code == 1

    # try new folder, should fail because the datapool config folder was created before:
    non_existing_folder = tmpdir.join("landing_zone_0").mkdir().strpath
    result = runner.invoke(init_config, [non_existing_folder])

    output = result.output.strip()
    assert fnmatch(output, "*datapool folder * already exists"), output

    assert result.exit_code == 1


def test_init_db(data_path):

    from datapool.main import init_db

    runner = CliRunner()
    result = runner.invoke(init_db, [])
    assert result.exit_code == 0, result.output + str(result.exception)

    # should fail: can not init same db again
    runner = CliRunner()
    result = runner.invoke(init_db, [])
    assert result.exit_code == 1

    # should fail, one "--force" is not enough
    result = runner.invoke(init_db, ["--force"])
    assert result.exit_code == 1

    # should succed: we agree to overwrite existing db
    result = runner.invoke(init_db, ["--force", "--force"])
    assert result.exit_code == 0


def test_start_develop(data_path, tmpdir, monkeypatch):
    monkeypatch.setenv("ETC", tmpdir.strpath)

    from datapool.main import start_develop, init_config

    runner = CliRunner()

    fresh_landing_zone = tmpdir.join("landing_zone").mkdir().strpath
    result = runner.invoke(init_config, [fresh_landing_zone])
    assert result.exit_code == 0, result.output

    runner = CliRunner()
    result = runner.invoke(start_develop, [tmpdir.join("test_start_develop").strpath])
    assert result.exit_code == 0, result.output + str(result.exception)


def test_update_operational(data_path, tmpdir, monkeypatch):

    from datapool.main import update_operational, start_develop, init_config

    monkeypatch.setenv("ETC", tmpdir.strpath)

    runner = CliRunner()

    fresh_landing_zone = tmpdir.join("landing_zone").mkdir().strpath
    result = runner.invoke(init_config, [fresh_landing_zone])
    assert result.exit_code == 0, result.output

    result = runner.invoke(start_develop, [tmpdir.join("test_start_develop").strpath])
    assert result.exit_code == 0, result.output + str(result.exception)

    # no assert for return code. might fail or not depending on matlab availability
    runner.invoke(update_operational, [tmpdir.join("test_start_develop").strpath])


def test_check(data_path, tmpdir, monkeypatch):

    from datapool.main import check, start_develop, init_config

    monkeypatch.setenv("ETC", tmpdir.strpath)

    runner = CliRunner()

    fresh_landing_zone = tmpdir.join("landing_zone").mkdir().strpath
    result = runner.invoke(init_config, [fresh_landing_zone])
    assert result.exit_code == 0, result.output

    result = runner.invoke(start_develop, [tmpdir.join("test_start_develop").strpath])
    assert result.exit_code == 0, result.output + str(result.exception)

    # no assert for return code. might fail or not depending on matlab availability
    runner.invoke(check, [tmpdir.join("test_start_develop").strpath])


@pytest.mark.skipif(not has_matlab, reason='needs matlab to work')
def test_all(regtest_print, tmpdir, monkeypatch):

    import signal

    from datapool.main import (init_config, init_db, create_example, update_operational,
                               delete_entity, check_config, check, delete_signals)

    monkeypatch.setenv("ETC", tmpdir.strpath)

    runner = CliRunner()

    fresh_landing_zone = tmpdir.join("landing_zone").mkdir().strpath
    dlz = tmpdir.join("dlz")

    def invoke(cmd, args=(), assert_fail=False):
        result = runner.invoke(cmd, args, catch_exceptions=False)
        print(result.output)
        regtest_print(result.output.rstrip())
        if assert_fail:
            assert result.exit_code != 0, result.output
        else:
            assert result.exit_code == 0, result.output

    invoke(init_config, [fresh_landing_zone, '--use-sqlitedb'])
    invoke(init_db)
    invoke(check_config)
    invoke(create_example, [dlz.strpath])
    invoke(check, [dlz.strpath])

    def start_bg_server():

        proc = subprocess.Popen(['pool', 'run-simple-server'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

        for line in iter(proc.stdout.readline, b""):
            if line.startswith(b"- observe"):
                # server startup finihsed
                break
        return proc

    def wait_for_conversion_finishes(proc):
        for line in iter(proc.stdout.readline, b""):
            line = str(line, 'utf-8').rstrip()
            print(line)
            if re.match("timing: this is \d+ signals per second", line.strip()):
                print("BREAK")
                break

    proc = start_bg_server()

    try:
        invoke(update_operational, [dlz.strpath])
        shutil.copy(dlz.join(
                'data/sensor_from_company_xyz/sensor_instance_matlab/raw_data/data-001.raw'
                ).strpath,
            tmpdir.join(
                'landing_zone/data/sensor_from_company_xyz/sensor_instance_matlab/raw_data'
                ).strpath
            )
        wait_for_conversion_finishes(proc)
        # patch getuid, to make delete command work
        os.getuid = lambda: 0
        invoke(delete_signals, ["timestamp>=2000-01-01:00:00:00,parameter==Flow"])
        invoke(delete_signals, ['--force', '--force', "timestamp>=2000-01-01:00:00:00,parameter==Flow"])
        invoke(delete_entity, ['--what', 'site', 'test_site'])
        invoke(delete_entity, ['--force', '--force', '--what', 'site', 'test_site'])
        invoke(update_operational, [dlz.strpath], assert_fail=True)

    finally:
        os.kill(proc.pid, signal.SIGHUP)
        print('killed server')
