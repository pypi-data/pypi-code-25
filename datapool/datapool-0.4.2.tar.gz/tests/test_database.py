# encoding: utf-8
from __future__ import print_function, division, absolute_import

from .test_site_model import load_sites
from datapool.database import (setup_db, setup_fresh_db, dump_db, check_if_tables_exist, copy_db,
                               filters_to_sqlalchemy_expression)
from datapool.errors import InvalidOperationError
from datapool.site_and_picture_model import check_and_commit
from datapool.config_handling import config_for_develop_db

import pytest


def test_setup_db(config, setup_logger):

    with pytest.raises(InvalidOperationError):
        setup_fresh_db(config.db)

    setup_db(config.db)
    assert check_if_tables_exist(config.db)

    with pytest.raises(InvalidOperationError):
        setup_db(config.db)

    setup_fresh_db(config.db)


def test_copy_db(config, lz, regtest, setup_logger, tmpdir):

    engine = setup_db(config.db)
    excs, (site, ) = load_sites(lz)
    assert not excs
    check_and_commit(site, engine)
    dump_db(config.db, file=regtest)

    config_develop_db, __ = config_for_develop_db(tmpdir.strpath)

    # the target table does not exist, but delete_existing=True should still work in this
    # case
    for name in copy_db(config.db, config_develop_db, delete_existing=True, copy_signals=True):
        print("copy", name, file=regtest)
    dump_db(config.db, file=regtest)

    # now we try to overwrite existing tables:
    with pytest.raises(InvalidOperationError):
        for __ in copy_db(config.db, config_develop_db, delete_existing=False, copy_signals=True):
            pass

    # now we enforce overwriting existing data:
    for __ in copy_db(config.db, config_develop_db, delete_existing=True, copy_signals=True):
        pass
    dump_db(config.db, file=regtest)


def test_filters_to_sqlalchemy_expression(regtest):
    all_filters = [["timestamp > 2017, site==abc"],
                   ["timestamp <= 2017, site==abc", "x==7"],
                   ["timestamp > 2017, source==abc"],
                   ["timestamp >= 2017, parameter==a"],

                   ["timestamp, parameter==a"],
                   ["timestamp != 2017, parameter==a"],
                   ["timestamp == 2017-13, parameter==a"],
                   ["timestamp == 2017-13, invalid_field==a"],
                   ]

    for filters in all_filters:
        print(filters, file=regtest)
        expression, messages = filters_to_sqlalchemy_expression(filters)
        for message in messages:
            print(message, file=regtest)
        if expression is not None:
            print(expression, expression.compile().params, file=regtest)
        print(file=regtest)
