#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Victor Calderon
# Created      : 2018-05-02
# Last Modified: 2018-05-02
from __future__ import print_function, division, absolute_import
__author__     =['Victor Calderon']
__copyright__  =["Copyright 2018 Victor Calderon"]
__email__      =['victor.calderon@vanderbilt.edu']
__maintainer__ =['Victor Calderon']
__all__        =[   "Program_Msg",
                    "Index",
                    "get_immediate_subdirectories",
                    "Path_Folder",
                    "File_Exists",
                    "File_Download_needed"]
"""
Utilities for verifying file existence, directory paths, etc.
"""

## Import modules
import os
import sys
import subprocess
import time
import traceback
import numpy as np
from   pathlib import Path
from   cosmo_utils.custom_exceptions import LSSUtils_Error

## Functions

# Message for a filename. It displays the basename of the filename
def Program_Msg(filename):
    """
    Program message for `filename`

    Parameters
    ----------
    filename : string
        Path to the filename being used

    Returns
    ----------
    Prog_msg : string
        String message for given `filename`
    """
    try:
        assert(os.path.exists(filename))
        # Creating message
        Prog_msg = '\n\t\t==> {} >>> '.format(os.path.basename(filename))
    except:
        msg = '>>> `filename` {} not found! Exiting!'.format(filename)
        raise ValueError(msg)

    return Prog_msg

## Compiles the array of files with matching pattern
def Index(pathdir, datatype, sort=True, basename=False):
    """
    Indexes the files in a directory `pathdir` with a specific data type
    `datatype`.

    Parameters
    ----------
    pathdir : string
        Path to the directory being analyzed

    datatype : string
        Type of documents to look for.

    sort : `bool`, optional (default = True)
        If this is set to True, the output list is sorted by name

    basename : `bool`, optional
        If this is set to True, the output list will contain only the 
        basename of the files in `pathdir`

    Returns
    ----------
    file_arr : np.ndarray
        List of (sorted) files in `pathdir` with datatype `.datatype`
    """
    # Checking that directory exists
    if os.path.exists(pathdir):
        # List of files
        Path_obj = Path(os.path.abspath(pathdir))
        file_arr = list(Path_obj.rglob('*{0}'.format(datatype)))
        file_arr = np.array([x.as_posix() for x in file_arr])
        # Sorting
        if sort:
            file_arr = np.sort(file_arr)
        # Basenames
        if basename:
            file_arr = np.array([os.path.basename(x) for x in file_arr])
    else:
        msg = '{0} `pathdir` {1} not found!'.format(Program_Msg(__file__),
            pathdir)
        raise LSSUtils_Error(msg)

    return file_arr

## Immediate subdirectories for a given directory
def get_immediate_subdirectories(pathdir, sort=True):
    """
    Immediate subdirectories to a given directory path

    Parameters
    ----------
    pathdir : str
        Path to the desired directory

    Returns
    ----------
    subdir_arr : array_like or array of strings
        Array of paths of subdirectories of `pathdir`

    sort : `bool`, optional (default = True)
        If this is set to True, the output list is sorted by name
    """
    if os.path.exists(pathdir):
        Path_obj   = Path(pathdir)
        # List of subdirectories
        subdir_arr = np.array([x for x in os.listdir(pathdir) \
                                if (os.path.isdir(str(Path_obj.joinpath(x))) and 
                                    ('__' not in x))])
        if sort:
            subdir_arr = np.sort(subdir_arr)
    else:
        msg = '{0} `pathdir` {1} not found!'.format(Program_Msg(__file__),
            pathdir)
        raise LSSUtils_Error(msg)

    return subdir_arr

## Creates a Folder if needed
def Path_Folder(pathdir, time_sleep=0.5):
    """
    Creates a folder if it does not exist already

    Parameters
    ----------
    pathdir : str
        Path to the desired directory

    time_sleep : float, optional
        Amount of time in seconds to `sleep` or wait for the process to 
        finish. By default `time_slee` is set to 0.5 seconds.
    """
    if os.path.exists(pathdir):
        pass
    else:
        while True:
            try:
                os.makedirs(directory)
                break
            except OSError as e:
                if e.errno != 17:
                    raise
                ## Adjusting time_sleep
                time.sleep(time_sleep)
                pass

## Checking if a file exists
def File_Exists(filename):
    """
    Detrmines if file exists or not

    Parameters
    -----------
    filename : str
        Absolute path to the file

    Raises
    -----------
    LSSUtils_Error : Exception
    """
    if os.path.exists(os.path.abspath(filename)):
        try:
            assert(os.path.isfile(os.path.abspath(filename)))
        except:
            msg = '{0} `filename` {1} not found!'.format(Program_Msg(__file__),
                filename)
            raise LSSUtils_Error(msg)
    else:
        msg = '{0} `filename` {1} not found!'.format(Program_Msg(__file__),
            filename)
        raise LSSUtils_Error(msg)

## Downloading a file from a remote server
def File_Download_needed(localpath, remotepath):
    """
    Determines if there exists a local copy of a file.
    If not, the file is downloaded from the remote server and a copy of 
    the file is saved locally

    Parameters
    ----------
    localpath : str
        Local path to the file.

    remotepath : str
        Remote path to the file. This is the URL of the file, if there is 
        no local copy of the file
    """
    file_msg = Program_Msg(__file__)
    # File extension - Remotely
    web_ext = os.path.splitext(remotepath)[1]
    # Checking if there is a local copy of the file
    if (os.path.exists(localpath) and os.path.isfile(localpath)):
        pass
    else:
        ## Downloading file
        # Testing for different kinds of files
        if web_ext == '.gz':
            cmd = 'wget {0} -O {0}{1}'.format(remotepath, localpath, web_ext)
            print('{0} {1}'.format(file_msg, cmd))
            subprocess.call(cmd, shell=True)
            # Unzipping file
            cmd = 'gzip -d {0}'.format(localpath + web_ext)
            print('{0} {1}'.format(file_msg, cmd))
            subprocess.call(cmd, shell=True)
        if web_ext == '.tar':
            cmd = 'wget {0} -O {0}{1}'.format(remotepath, localpath, web_ext)
            print('{0} {1}'.format(file_msg, cmd))
            subprocess.call(cmd, shell=True)
            # Unzipping file
            local_dir = os.path.dirname(localpath)
            cmd = 'tar zxf {0} - C {1}'.format(localpath + web_ext, local_dir)
            print('{0} {1}'.format(file_msg, cmd))
            subprocess.call(cmd, shell=True)
        else:
            cmd = 'wget {0} -O {1}'.format(remotepath, localpath)
            print('{0} {1}'.format(file_msg, cmd))
            subprocess.call(cmd, shell=True)
    ##
    ## Checking that file exists
    File_Exists(localpath)

