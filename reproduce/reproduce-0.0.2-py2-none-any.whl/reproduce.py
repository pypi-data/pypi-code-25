"""Framework for reproducible computational science."""
import shutil
import os
import errno
import logging
import future.moves.urllib.request

CACHE_DIR = 'cache'
DATA_DIR = 'data'
DOC_DIR = 'doc'
LOGS_DIR = 'logs'
MUNGE_DIR = 'munge'
REPORTS_DIR = 'reports'

ALL_DIR_LIST = [
    CACHE_DIR, DATA_DIR, DOC_DIR, LOGS_DIR, MUNGE_DIR, REPORTS_DIR]


def url_fetcher(url):
    """Closure for retrieving a url."""
    def _url_fetcher(path):
        """Download `url` to `path`."""
        response = future.moves.urllib.request.urlopen(url)
        with open(path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        response.close()
    return _url_fetcher


class Reproduce(object):
    """Object to initialize and store state of reproduction library."""

    def __init__(self, root_path):
        """Initialize directory structure."""
        logger = logging.getLogger('reproduce.Reproduce.init')
        self.dir_root_map = {}
        for dir_path in ALL_DIR_LIST:
            try:
                self.dir_root_map[dir_path] = os.path.join(
                    root_path, dir_path)
                os.makedirs(self.dir_root_map[dir_path])
                logger.info('%s created', dir_path)

            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                else:
                    logger.info('%s already exists', dir_path)

        self.id_data_map = {}

    def __getitem__(self, data_id):
        """Given a `data_id` from `register_data` returns data value."""
        return self.id_data_map[data_id]

    def register_data(
            self, data_id, expected_path, constructor_func=None):
        """Register a data file and create it if it doesn't exist.

        Parameters:
            data_id (str): a unique  identifier for this data that can
                be used later to index back into the Reproduce object.
            expected_path (str): path to the expected file within the
                DATA_DIR directory.
            constructor_func (func): a function with a path argument to
                invoke if the file does not already exist. This function
                will be called with the effective path passed to it.

        Returns:
            None.

        """
        logger = logging.getLogger('reproduce.Reproduce.register_data')
        full_path = os.path.join(self.dir_root_map['data'], expected_path)
        try:
            dir_path = os.path.dirname(full_path)
            os.makedirs(dir_path)
            logger.info('%s created', dir_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        if not os.path.exists(full_path):
            if constructor_func is None:
                raise ValueError(
                    '%s does not exist and data constructor not provided' %
                    full_path)
            logger.info('%s does not exist, invoking data constructor')
            constructor_func(full_path)
        self.id_data_map[data_id] = full_path
