from __future__ import division

import os
import itertools
import logging
import re


logger = logging.getLogger(__name__)


def get_volume(path):
    """Get the underlying volume from a path.

    :param path: the path to evaluate
    :returns: the path to the volume
    :rtype: str

    """
    abspath = os.path.abspath(path)
    while not os.path.ismount(abspath):
        abspath = os.path.dirname(abspath)
    return abspath


def validate_same_volume(paths):
    """Given a list of paths make sure they're
    part of the same volume.

    :param paths: List of paths to validate
    :returns: True if same volume, else False
    :rtype: bool

    """
    volumes = set([
        get_volume(path)
        for path in paths
    ])
    return len(volumes) == 1


def get_percentage(path):
    """Get current volume percentage of path.

    :param path: Filesystem path
    :returns: Volume usage percentage
    :rtype: float

    """
    stat = os.statvfs(path)
    usage = ((stat.f_blocks - stat.f_bavail) / stat.f_blocks) * 100
    return usage


def files_in_dir(d, include=[]):
    """Get a recursive list of files in a directory with mtimes.

    :param d: The directory to walk
    :param include: List of regexes that should be evaluated to include
    :returns: yields the mtime and path
    :rtype:

    """
    for root, directory, paths in os.walk(d):
        for path in paths:
            full_path = os.path.join(root, path)
            if include:
                matches = [
                    re.search(search, full_path)
                    for search in include
                ]
                if any(matches):
                    yield (os.path.getmtime(full_path), full_path,)
            else:
                yield (os.path.getmtime(full_path), full_path,)


def clean_directories(dirs, percentage, include=[]):
    """Given a list of directories and percentages, and an optional
    list of include regexes, try to clean out the directory so that
    the new percentage is reached. This function makes the assumption
    that the directories provided are on the same volume. So be
    sure to call validate_same_volume on the passed in
    directories first.

    This function will return True if successful, otherwise False.

    :param dirs: Directories to clean
    :param percentage: Percentage to try to clean to
    :param include: Regex filters of paths to include
    :returns: True if cleanup was successful, otherwise False
    :rtype: bool

    """
    files = sorted(list(set(itertools.chain(*[
        files_in_dir(d, include)
        for d in dirs
    ]))))

    for mtime, path in files:
        if get_percentage(dirs[0]) <= percentage:
            return True
        else:
            logger.debug('Removing %s.', path)
            os.unlink(path)

    if get_percentage(dirs[0]) > percentage:
        return False

    return True
