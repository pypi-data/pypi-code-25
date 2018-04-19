""" This module contains commons methods which has no dependencies (except for
the base python library) and thus are usable in every part of the software.

The methods included in this modules are all file-related functions.
"""
import mmap
import os
import os.path


def line_count(file_path: str) -> int:
    """ Efficiently count the number of lines in a file.
    If possible, the UNIX command `wc -l` must be used instead (as its much
    faster).
    """
    f = open(file_path, "r+")
    buf = mmap.mmap(f.fileno(), 0)
    lines = 0
    readline = buf.readline
    while readline():
        lines += 1
    return lines


def delete_existing_files(*file_pathes):
    """ Delete all files passed as parameters. """
    for filepath in file_pathes:
        if os.path.isfile(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    pass
