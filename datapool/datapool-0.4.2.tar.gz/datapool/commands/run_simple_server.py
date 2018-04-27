import os
import queue
import signal

from ..config_handling import read_config
from ..database import setup_db, check_if_tables_exist
from ..dispatcher import Dispatcher
from ..errors import InvalidOperationError
from ..landing_zone_structure import lock_file
from ..logger import get_cmdline_logger
from ..observer import CREATED_EVENT, MODIFIED_EVENT, start_observer, shutdown_observer
from ..utils import write_pid_file, remove_pid_file


def run_simple_server(verbose, print_ok, print_err, still_running=None):

    config = read_config()
    if config is None:
        print_err("- no config file found. please run 'pool init-config' first.")
        return 1

    with get_cmdline_logger(verbose):

        try:
            already_setup = check_if_tables_exist(config.db)
        except InvalidOperationError as e:
            print_err("+ can not check database: {}".format(e))
            return 1
        if not already_setup:
            print_ok("- setup fresh db")
            try:
                setup_db(config.db, verbose=verbose)
            except InvalidOperationError as e:
                print_err("+ can not setup database: {}".format(e))
                return 1
        else:
            print_ok("- db already setup")

        if config.julia.executable:

            print_ok("- check startup julia")
            from datapool.julia_runner import JuliaRunner
            r = JuliaRunner(config.julia.executable)
            r.start_interpreter()
            ok = r.is_alive()
            if not ok:
                print_err("+ julia startup failed")
                return 1

        setup = _setup_simple_server(config, print_ok, print_err, still_running)
        if setup is None:
            return 1
        print_ok("- observe {} now".format(config.landing_zone.folder))
        _simple_server_loop(still_running, setup, config, print_ok, print_err)

    print_ok("+ done", fg="green")

    return 0


def _setup_simple_server(config, print_ok, print_err, still_running):

    dispatcher = Dispatcher(config)
    q = queue.Queue()
    root_folder = config.landing_zone.folder

    def call_back(event, rel_path):
        if event not in (CREATED_EVENT, MODIFIED_EVENT):
            if rel_path == lock_file:
                print_ok("- removed update lock for landing zone")
            else:
                if not os.path.basename(rel_path).startswith("."):
                    print_err("- invalid event for {}".format(rel_path))
        else:
            if rel_path == lock_file:
                print_ok("- lock landing zone for updating")
            else:
                q.put((event, rel_path))

    try:
        observer = start_observer(root_folder, call_back)
    except Exception as e:
        print_err("- could not start observer: {}".format(e))
        return None

    return q, dispatcher, observer


def _simple_server_loop(still_running, setup, config, print_ok, print_err):

    q, dispatcher, observer = setup

    def shutdown(signum=None, frame=None):
        nonlocal old_handler
        nonlocal still_running
        print()
        if signum is not None:
            print_ok("- shutdown observer due to signal {}".format(signum))
        else:
            print_ok("- shutdown observer")
        shutdown_observer(observer)
        if signum is not None and callable(old_handler):
            old_handler(signum, frame)
        still_running = lambda: False

    old_handler = signal.signal(signal.SIGTERM, shutdown)

    try:
        write_pid_file(config)
        while still_running is None or still_running():
            try:
                event, rel_path = q.get(timeout=.01)
            except queue.Empty:
                continue

            # we ignore dot files:
            if os.path.basename(rel_path).startswith("."):
                continue

            print_ok("- dispatch {}".format(rel_path))
            results = dispatcher.dispatch(rel_path)
            for result in results:
                if isinstance(result, str):
                    print_ok("  {}".format(result))
                else:
                    print_err("  error: {}".format(result))
            print_ok("  dispatch done")

    except KeyboardInterrupt:
        shutdown()
    finally:
        remove_pid_file(config)
