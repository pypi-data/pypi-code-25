# Copyright 2018 Robert Haas
# For license information, see LICENSE.TXT in the package root directory

import errno as _errno
import os as _os
import re as _re
import socket as _socket
from pprint import pprint as _pprint
from time import sleep as _sleep


def _verify_address(address):
    """
    Check if an address is valid, i.e. has the form 'ip:port' or 'protocol://ip:port'

    Example:
        >>> _verify_address('127.0.0.1:7077')
    """
    if not _re.match(r'([\w\d_-]+://)?[0-9]+(?:\.[0-9]+){3}:[0-9]+', address):
        raise ValueError('Invalid address: "{}"\n'
                         'It needs to be of the form "ip:port" or '
                         '"protocol://ip:port"'.format(address))


def _parse_address(address):
    """
    Split an address of form 'ip:port' or 'protocol://ip:port' into its constituents
    """
    parts = address.split(':')
    if len(parts) == 2:
        address, port = parts
        protocol = None
    elif len(parts) == 3:
        protocol, address, port = parts
        address = address.lstrip('/')
    return protocol, address, port


def _is_address_in_use(address):
    """
    Check if an address is already in use by another process.

    References:
        - https://stackoverflow.com/questions/2470971/fast-way-to-test-if-a-port-is-in-use-using-python
    """
    _, address, port = _parse_address(address)
    port = int(port)
    skt = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    try:
        skt.bind((address, port))
    except _socket.error as err:
        if err.errno == _errno.EADDRINUSE:
            return True
    except Exception:
        pass
    finally:
        skt.close()
    return False


class _DaskSetup:
    """
    Setup Dask for distributed computing on a cluster.

    References:
        - Dask's command line interface

            - http://dask.pydata.org/en/latest/setup/cli.html
            - https://distributed.readthedocs.io/en/latest/setup.html#using-the-command-line

        - Programmatic use of Dask

            - http://dask.pydata.org/en/latest/setup/python-advanced.html
            - http://distributed.readthedocs.io/en/latest/setup.html#using-the-python-api
            - http://distributed.readthedocs.io/en/latest/api.html
            - http://www.tornadoweb.org/en/stable/ioloop.html
    """
    def __init__(self):
        self._connection = None
        self._scheduler = None
        self._worker = None

    def start_scheduler(self, scheduler_address):
        """
        Start a scheduler process. It occupies the Python interpreter until stopped externally.

        Args:
            scheduler_address: Desired scheduler address of the form 'ip-address:port'

        Raises:
            ConnectionError: If scheduler can not be started with the given address.

        Example:
            >>> start_scheduler('127.0.0.1:8791')

        Note:
            A scheduler process can also be started with Dask's command line interface,
            for example::

                $ dask-scheduler --host 127.0.0.1 --port 8791

        References:
            - http://distributed.readthedocs.io/en/latest/scheduling-state.html#distributed.scheduler.Scheduler
            - http://www.tornadoweb.org/en/stable/ioloop.html#tornado.ioloop.IOLoop.handle_callback_exception
        """
        # TODO: provide all available arguments explicitely
        # TODO: stop scheduler at STRG+C but enable restart in the same python process,
        #       needs correct handling of tornado loop
        # TODO: Stop is not guaranteed because finally is not necessarily executed (e.g. SIGTERM)

        from dask import distributed
        from tornado.ioloop import IOLoop

        # Precondition
        _verify_address(scheduler_address)
        if _is_address_in_use(scheduler_address):
            raise ConnectionError('Adress is already in use by another process.')

        # Start scheduler and stop it afterwards
        try:
            self._scheduler = distributed.Scheduler()
            self._scheduler.start(scheduler_address)
            loop = IOLoop.current()

            def silent_callback_excpt_handler(*irrelevant_args, **irrelevant_kwargs):
                pass
            loop.handle_callback_exception = silent_callback_excpt_handler
            loop.start()
        except Exception as err1:
            raise ConnectionError(err1)
        finally:
            # Ensure stop of scheduler
            try:
                self._scheduler.close()
            except Exception as err2:
                print(err2)
            # Ensure stop of loop
            try:
                loop.stop()
            except Exception as err3:
                print(err3)

    def start_worker(self, scheduler_address, max_memory='auto', num_cores=1):
        """
        Start a worker process. It occupies the Python interpreter until stopped externally.

        Args:
            scheduler_address: Address of running scheduler of the form 'ip-address:port'
            max_memory (optional): Amount of memory that this worker may use. Can be number of
                bytes (0 = no limit), 'auto' for 60% of memory or a string like '5GB'
            num_cores (optional): Number of cores that this worker will use

        Example:
            >>> start_worker('127.0.0.1:8791')

        Note:
            A worker process can also be started with Dask's command line interface,
            for example::

                $ dask-worker '127.0.0.1:8791'

        Warning:
            Prevent crashes:
            Be careful with having a memory limit when using a Nanny process
            (CLI does so automatically):
            "At 95% memory load a worker’s nanny process will terminate it. This is to avoid
            having our worker job being terminated by an external job scheduler
            (like YARN, Mesos, SGE, etc.)."

        References:
            - http://distributed.readthedocs.io/en/latest/worker.html
            - http://distributed.readthedocs.io/en/latest/worker.html#command-line-tool
            - http://distributed.readthedocs.io/en/latest/worker.html#distributed.worker.Worker
            - http://www.tornadoweb.org/en/stable/ioloop.html#tornado.ioloop.IOLoop.handle_callback_exception
        """
        # TODO: stop worker (with disconnect shown at scheduler) but enable restart in the same
        #       python process (currently: "ValueError: I/O operation on closed file") due to close
        #       of loop
        # TODO: Alternatively, replace Worker with Nanny if you want your workers to be managed
        #       in a separate process by a local nanny process.

        from dask import distributed
        from tornado.ioloop import IOLoop

        # Precondition
        _verify_address(scheduler_address)
        # Problem: probably works only locally
        # if not _is_address_in_use(scheduler_address):
        #     raise ConnectionError('Scheduler seems unavailable. '
        #                           'Address is not in use by another process.')

        # Start worker and stop it afterwards
        try:
            self._worker = distributed.Worker(scheduler_address,
                                              memory_limit=max_memory, ncores=num_cores)
            self._worker.start()
            loop = IOLoop.current()

            def silent_callback_excpt_handler(*irrelevant_args, **irrelevant_kwargs):
                pass
            loop.handle_callback_exception = silent_callback_excpt_handler
            loop.start()
        except Exception as err1:
            raise ConnectionError(err1)
        finally:
            # Ensure stop of scheduler
            try:
                self._worker.close()
            except Exception as err2:
                print(err2)
            # Ensure stop of loop
            try:
                loop.close()
            except Exception as err3:
                print(err3)

    def connect_to_scheduler(self, scheduler_address):
        """
        Start a connection to a running scheduler. The Python interpreter is not occupied.

        Args:
            scheduler_address: Address of running scheduler of the form 'ip-address:port'

        Example:
            >>> connect_to_scheduler('127.0.0.1:8791')

        References:
            - http://distributed.readthedocs.io/en/latest/client.html
            - http://distributed.readthedocs.io/en/latest/api.html#distributed.client.Client
        """
        from dask import distributed

        # Precondition
        _verify_address(scheduler_address)

        # Establish connection
        try:
            self._connection = distributed.Client(scheduler_address)
        except Exception as err:
            raise ConnectionError('Could not connect to scheduler. Did you start it? '
                                  'Is it still running? Is the address correct?\n{}'.format(err))

    def report_status(self):
        """
        Print information about the current cluster setup and status of the system.

        References:
            - http://distributed.readthedocs.io/en/latest/api.html#distributed.client.Client.get_versions
            - http://distributed.readthedocs.io/en/latest/api.html#distributed.client.Client.profile
            - http://distributed.readthedocs.io/en/latest/api.html#distributed.client.Client.scheduler_info
        """
        # TODO: report most relevant information in nice format

        if self._connection is None:
            print('Not connected to a scheduler.')
        else:
            _pprint(self._connection.scheduler_info())
            # _pprint(self._connection.get_versions())
            # _pprint(self._connection.profile())


class _SparkSetup:
    """
    Setup Apache Spark (Python bindings via pyspark) for distributed computing on a Cluster.

    References:
        - Apache Spark's command line interface

            - https://spark.apache.org/docs/latest/#launching-on-a-cluster
            - https://spark.apache.org/docs/latest/cluster-overview.html
            - https://spark.apache.org/docs/latest/spark-standalone.html#starting-a-cluster-manually

        - Programmatic use of Apache Spark via pyspark

            - http://spark.apache.org/docs/2.2.0/api/python/index.html
    """
    def __init__(self):
        self._connection = None
        self._scheduler = None
        self._worker = None

    @staticmethod
    def _ensure_prefixed_address(address):
        """Add 'spark://' prefix to an address if it is missing"""
        prefix = 'spark://'
        if not address.startswith(prefix):
            address = prefix + address
        return address

    def start_scheduler(self, scheduler_address):
        """
        Start a scheduler process. It occupies the Python interpreter until stopped externally.

        Args:
            scheduler_address: Desired scheduler address of the form 'ip-address:port'

        Example:
            >>> start_scheduler('127.0.0.1:7077')

        Note:
            A scheduler process can also be started with Apache Spark's command line interface,
            for example::

                $ $SPARK_HOME/sbin/start-master.sh --host 127.0.0.1 --port 7077

            It needs to be stopped afterwards::

                $ $SPARK_HOME/sbin/stop-master.sh

            The status can be monitored in a Webbrowser at http://localhost:8080 or another
            reported address.
        """
        # TODO: get rid of dangerous os call, see if there's programmatic access via pyspark

        # Precondition
        _verify_address(scheduler_address)
        if _is_address_in_use(scheduler_address):
            raise ConnectionError('Adress is already in use by another process.')
        scheduler_address = self.__class__._ensure_prefixed_address(scheduler_address)
        protocol, address, port = _parse_address(scheduler_address)

        # Start scheduler and stop it afterwards
        try:
            _os.system('$SPARK_HOME/sbin/stop-master.sh')
            _os.system('$SPARK_HOME/sbin/start-master.sh --host {} --port {}'.format(
                address, port))
            while True:
                _sleep(1)
        finally:
            _os.system('$SPARK_HOME/sbin/stop-master.sh')

    def start_worker(self, scheduler_address):
        """
        Start a worker process. It occupies the Python interpreter until stopped externally.

        Args:
            scheduler_address: Address of running scheduler of the form 'ip-address:port'

        Example:
            >>> start_worker('127.0.0.1:7077')

        Note:
            A worker process can also be started with Apache Spark's command line interface,
            for example::

                $ $SPARK_HOME/sbin/start-slave.sh spark://127.0.0.1:7077 --work-dir $HOME/temp_spark_worker

            It needs to be stopped afterwards::

                $ $SPARK_HOME/sbin/stop-slave.sh
        """
        # TODO: decide if work_dir is specified --work-dir $HOME/temp_spark_worker
        # TODO: find out if there is a programmatic way to start workers (instead of os call)

        # Precondition
        _verify_address(scheduler_address)
        # Problem: probably works only locally
        # if not _is_address_in_use(scheduler_address):
        #     raise ConnectionError('Scheduler seems unavailable. '
        #                           'Address is not in use by another process.')
        scheduler_address = self.__class__._ensure_prefixed_address(scheduler_address)

        # Start worker and stop it afterwards
        try:
            _os.system('$SPARK_HOME/sbin/stop-slave.sh')
            _os.system('$SPARK_HOME/sbin/start-slave.sh "{}"'.format(scheduler_address))
            while True:
                _sleep(1)
        finally:
            _os.system('$SPARK_HOME/sbin/stop-slave.sh')

    def connect_to_scheduler(self, scheduler_address):
        """
        Start a connection to a running scheduler. The Python interpreter is not occupied.

        Args:
            scheduler_address: Address of running scheduler of the form 'ip-address:port'

        Example:
            >>> connect_to_scheduler('127.0.0.1:7077')

        References:
            - http://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.SparkContext
        """
        # TODO: ensure that there is no existing spark context by better means

        import pyspark

        # Precondition
        _verify_address(scheduler_address)
        scheduler_address = self.__class__._ensure_prefixed_address(scheduler_address)

        # Establish connection
        try:
            pyspark.SparkContext.getOrCreate().stop()
            self._connection = pyspark.SparkContext(
                master=scheduler_address, appName='unified_map')
            print('Interactive information at {}'.format(self._connection.uiWebUrl))
        except Exception as err:
            raise ConnectionError('Could not connect to scheduler. Did you start it? '
                                  'Is it still running? Is the address correct?\n{}'.format(err))

    def report_status(self, depth=None):
        """
        Print information about the current cluster setup and status of the system.

        References:
            - http://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.SparkContext
            - http://spark.apache.org/docs/latest/api/python/pyspark.html#pyspark.SparkContext.statusTracker
        """
        if self._connection is None:
            print('Not connected to a scheduler.')
        else:
            conf = self._connection.getConf()
            _pprint(conf.getAll(), depth=depth)


dask = _DaskSetup()
spark = _SparkSetup()
