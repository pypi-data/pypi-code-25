# encoding: utf-8
from __future__ import print_function, division, absolute_import

from datetime import datetime
import functools
import os
import shutil
import time

from .database import connect_to_db
from .data_conversion import ConversionRunner, SUPPORTED_EXTENSIONS
from .errors import DataPoolException, InvalidOperationError, FatalError
from .domain_objects import DomainObject
from .landing_zone_structure import (lookup_handler, script_paths_for_raw_file,
                                     source_yaml_path_for_script)

from .logger import logger
from .signal_model import (check_and_commit as check_and_commit_signals, check_signals_uniqueness)
from .uniform_file_format import to_signals
from .utils import iter_to_list
from .yaml_parsers import parse_source


def wait_until_exists(path, max_attempts=10, wait_interval=0.1):
    if not os.path.exists(path):
        for __ in range(max_attempts):
            if os.path.exists(path):
                return True
            time.sleep(wait_interval)
        return False
    return True


def log_unexpected_exceptions(function):
    @functools.wraps(function)
    def wrapped_function(*a, **kw):
        logger()
        try:
            return function(*a, **kw)
        except Exception as e:
            args = list("{!r}".format(arg) for arg in a)
            args += list("{}={!r}".format(k, v) for (k, v) in sorted(kw.items()))
            call_signature = "{}({})".format(function.__name__, ", ".join(args))
            logger().error("unexpected error '{}' when calling {}".format(e, call_signature))

    return wrapped_function


def default_time_provider():
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def measure_delay(path):
    """seconds from last modifiation to now, which measures delay between
    file modification to handling the changes"""
    now = time.time()
    if os.path.exists(path):
        return now - os.stat(path).st_mtime
    else:
        return 0   # only triggered in tests


class Dispatcher:

    def __init__(self, config, time_provider=default_time_provider):
        """
        time_provider arg allows patching for regression tests !
        """
        self.config = config
        self.time_provider = time_provider
        self.root_folder = config.landing_zone.folder
        self.conversion_runner = ConversionRunner(config)
        self.engine = connect_to_db(self.config.db)

    @iter_to_list
    def dispatch(self, rel_path):
        full_path = os.path.join(self.root_folder, rel_path)
        # sometimes we have delay between os events and actual "existance" on linux:
        ok = wait_until_exists(full_path)
        if not ok:
            raise FatalError("file {} detected  by observer, but does actually not exist"
                             .format(full_path))

        delay = measure_delay(full_path)
        yield "delay of dispatching {}: {:.1f} msec".format(rel_path, delay * 1000)
        if rel_path.endswith(".yaml"):
            yield from self.dispatch_yaml(rel_path)
        elif rel_path.endswith(".raw"):
            # sometimes we have delay between os events and actual "existance" on linux:
            yield from self.dispatch_raw_file_conversion(rel_path)
        elif any(rel_path.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
            # no dispatch because dispatch is triggered on .raw file creation, only backup:
            yield from self.backup(rel_path)
        else:
            yield "do not know how to process file {}".format(rel_path)

    def backup(self, rel_path, found_error=False):
        try:
            yield from self._backup(rel_path, found_error)
        except IOError as e:
            yield "backup of {} failed: {}".format(rel_path, e)

    def _backup(self, rel_path, found_error):
        if not self.config.backup_landing_zone.folder:
            yield "skip backup, no backup folder configured"
            return
        backup_path = os.path.join(self.config.backup_landing_zone.folder, rel_path)
        folder = os.path.dirname(backup_path)
        if not os.path.exists(folder):
            os.makedirs(folder)
            yield "created folder {}".format(folder)

        # add time stamp to make file unique and better searchable:
        backup_path += ".{}".format(self.time_provider())
        if found_error:
            backup_path += "-broken"

        shutil.copy(self.full_path(rel_path), backup_path)
        yield "copied {} to {}".format(rel_path, backup_path)

    def full_path(self, *a):
        return os.path.join(self.root_folder, *a)

    def rel_path(self, p):
        return os.path.relpath(p, self.root_folder)

    def dispatch_raw_file_conversion(self, rel_raw_file_path):
        raw_file_path = self.full_path(rel_raw_file_path)
        script_paths = script_paths_for_raw_file(raw_file_path)

        if len(script_paths) > 1:
            yield InvalidOperationError("multiple conversion scripts found for {}"
                                        .format(rel_raw_file_path))
            return

        if len(script_paths) == 0:
            yield InvalidOperationError("no conversion script found next to {}"
                                        .format(rel_raw_file_path))
            return

        found_error = False
        for log_function, msg in self.run_conversion(script_paths[0], raw_file_path):
            log_function(msg)
            if log_function.__name__ == "error":
                found_error = True
            yield msg
        yield from self.backup(rel_raw_file_path, found_error)

        os.remove(raw_file_path)

    def run_conversion(self, script_path, raw_file_path):
        """yields exceptions and/or tuples (log_function, msg)
        """
        rel_script_path = self.rel_path(script_path)
        rel_raw_file_path = self.rel_path(raw_file_path)

        info = logger().info
        error = logger().error

        yield info, "convert {} with {}".format(rel_raw_file_path, rel_script_path)

        started = time.time()
        try:
            rows = self.conversion_runner.run_conversion(script_path, raw_file_path)
        except DataPoolException as e:
            yield error, "converting {} with {} failed:".format(rel_raw_file_path, rel_script_path)
            yield error, "    {}".format(e)
            return
        needed = time.time() - started

        yield info, "timing: converting {} needed {:.2f} msec".format(rel_raw_file_path, 1000 * needed)
        yield info, "timing: this is {:.0f} signals per second".format(len(rows) / needed)

        source = next(parse_source(self.root_folder, source_yaml_path_for_script(script_path)))
        for row in rows:
            row["source"] = source.name

        started = time.time()
        signals = to_signals(rows)

        def report(errors, task):
            MAXE = 30
            too_many = len(errors) > MAXE
            orig_len = len(errors)
            errors = errors[:MAXE]
            yield error, "{} {} with {} failed".format(task, rel_raw_file_path, rel_script_path)
            for e in errors:
                yield error, "    {}".format(e)
            if too_many:
                msg = "skipped {} error messages".format(orig_len - MAXE)
                yield error, msg

        errors_0 = check_signals_uniqueness(signals)
        if errors_0:
            yield from report(errors_0, "checking")
        committed_signals, errors_1 = check_and_commit_signals(signals, self.engine)
        if errors_1:
            yield from report(errors_1, "committing")

        yield info, "timing: needed {:.0f} msec to check and commit {} signals"\
                    .format(1000 * needed, len(committed_signals))
        yield info, "timing: this is {:.0f} signals per second"\
                    .format(len(committed_signals) / needed)

    def dispatch_yaml(self, rel_path):
        handler = lookup_handler(rel_path)

        if handler is None:
            yield InvalidOperationError("don't know how to handle {}".format(rel_path))
            return

        ok = True
        domain_object = None
        for result in handler.parser(self.root_folder, rel_path):
            if isinstance(result, DomainObject):
                domain_object = result
                continue
            yield InvalidOperationError("when parsing {}: {}".format(rel_path, result))
            ok = False

        if not ok:
            return

        if domain_object is None:
            yield "nothing to commit"
            return

        try:
            committed = handler.committer(domain_object, self.engine)
            if committed:
                yield "commited changes"
            else:
                yield "nothing committed, possibly no update"
        except DataPoolException as e:
            yield e

        self.backup(rel_path)
