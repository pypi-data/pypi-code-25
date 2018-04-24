""""""
import os
import sys
import pickle
import logging

from six.moves import urllib

from .bunch import Bunch, bunchify, unbunchify
from .time import *


def maybe_mkdirs(path, is_file=False, exist_ok=True):
    """递归创建文件夹

    Args:
        path (str): 待创建的路径，递归创建
        is_file (bool): 是否为文件路径
        exist_ok (bool): 默认为 True

    Examples:

        >>> maybe_mkdirs('D:/Tmp/a/b/')
        'D:/Tmp/a/b/'
        >>> maybe_mkdirs('D:/Tmp/a/b/c.txt')
        'D:/Tmp/a/b/c.txt'
        >>> maybe_mkdirs('D:/Tmp/a/b/c', is_file=True)  # 假设 c 是一个无后缀文件
        'D:/Tmp/a/b/c'

    Returns:
        str
    """
    if is_file:
        dirs, filename = os.path.split(path)
        os.makedirs(dirs, exist_ok=exist_ok)
    else:
        os.makedirs(path, exist_ok=exist_ok)

    return path


def save_to_pickle(obj, filepath):
    """
    保存到 pickle 文件

    Args:
        obj: 需要保存的对象
        filepath(str): 文件名

    Returns:
        None

    """
    filepath = maybe_mkdirs(filepath, is_file=True)
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)


def load_from_pickle(filepath):
    """
    从 pickle 加载对象

    Args:
        filepath(str): 文件名

    Returns:

    """
    with open(filepath) as f:
        return pickle.load(f)


def set_logging_basic_config(**kwargs):
    """
    快速设置 logging.basicConfig

    Args can be specified:
        filename: Specifies that a FileHandler be created, using the specified
            filename, rather than a StreamHandler.
        filemode: Specifies the mode to open the file, if filename is specified
            (if filemode is unspecified, it defaults to 'a').
        format: Use the specified format string for the handler.
        datefmt: Use the specified date/time format.
        style: If a format string is specified, use this to specify the
            type of format string (possible values '%', '{', '$', for
            %-formatting, :meth:`str.format` and :class:`string.Template`
            - defaults to '%').
        level: Set the root logger level to the specified level.
        stream: Use the specified stream to initialize the StreamHandler. Note
            that this argument is incompatible with 'filename' - if both
            are present, 'stream' is ignored.
        handlers: If specified, this should be an iterable of already created
            handlers, which will be added to the root handler. Any handler
            in the list which does not have a formatter assigned will be
            assigned the formatter created in this function.

    Returns:
        None
    """
    if 'format' not in kwargs:
        kwargs['format'] = '[%(name)s] : %(asctime)s : %(levelname)s : %(message)s'
    if 'level' not in kwargs:
        kwargs['level'] = logging.INFO

    logging.basicConfig(**kwargs)


def get_filepath_recursive(dirpath, abspath=True, recursive=True):
    """获取目录下所有文件名 （默认递归）
        该函数主要用于需要一次性处理大量**相似文件**的情况

        该函数主要利用 `os.walk(path)` 实现，
        该函数会递归遍历 path 下的所有文件夹，并返回一个生成器

    Args:
        dirpath (str): 文件夹路径
        abspath (bool): 是否返回绝对路径
        recursive (bool): 是否递归

    Examples:
        >>> fs_gen = get_filepath_recursive('D:/Tmp')

    Returns:
        list
    """
    fs = []
    if recursive:
        for root, _, files in os.walk(dirpath):
            if abspath:
                fs.extend((os.path.join(root, file) for file in files))
            else:
                fs.extend(files)
    else:
        if abspath:
            fs.extend((os.path.join(dirpath, file) for file in os.listdir(dirpath)))
        else:
            fs.extend(os.listdir(dirpath))

    return fs


def maybe_download(url, to_path='D:/Tmp', filename=None, expected_byte=None):
    """下载文件到指定目录

    Args:
        url (str): 文件下载路径
        to_path (str): 下载到本地路径
        filename (str): 重命名文件
        expected_byte (int): 文件预期大小

    Returns:
        str: filepath

    Examples:

        >>> url = 'http://mattmahoney.net/dc/bbb.zip'
        >>> filepath = maybe_download(url, filename='b.zip')
        >>> fp = maybe_download(url, to_path='D:/Tmp/b', expected_byte=45370)

    """
    if filename is not None:
        filepath = os.path.join(maybe_mkdirs(to_path), filename)
    else:
        _, filename = os.path.split(url)
        filepath = os.path.join(maybe_mkdirs(to_path), filename)

    if not os.path.exists(filepath):
        urllib.request.urlretrieve(url, filepath)
        logging.info('File is downloading.')

        if expected_byte is not None:
            file_size = os.stat(filepath).st_size
            if file_size != expected_byte:
                logging.info('File has been damage, please download it manually.')
    else:
        logging.info('File is ready.')

    return filepath


def cycle_iter(iterator):
    """
    无限循环迭代器

    Args:
        iterator (Iterable): 可迭代对象

    Examples:

        >>> it = cycle_iter([1, 2, 3])
        >>> for _ in range(4):
        ...     print(next(it))
        1
        2
        3
        1

    """
    # while True:
    #     yield from iter(iterator)
    from itertools import cycle
    return cycle(iterator)


def system_is_windows():
    """
    If the system is windows, return True

    Examples:
        >>> if system_is_windows():
        ...     print("Windows")
        Windows
    """
    import platform
    return platform.system() == "Windows"


is_windows_system = system_is_windows()


def get_logger(name=None, fname=None, mode='a', level=logging.INFO, stream=None,
               fmt="[%(name)s] : %(asctime)s : %(levelname)s : %(message)s"):
    """创建一个 logger
        默认 log to console，如果同时指定了 fname，还会将日志输出到文件

    Examples:
        >>> logger = get_logger("Test", stream=sys.stdout, fmt="[%(name)s] : %(levelname)s : %(message)s")
        >>> logger.info("test")
        [Test] : INFO : test

    """
    logger = logging.Logger(name)
    logger.setLevel(level)

    fmt = logging.Formatter(fmt)

    ch = logging.StreamHandler(stream)
    ch.setFormatter(fmt)

    logger.addHandler(ch)

    if fname is not None:
        fh = logging.FileHandler(fname, mode)
        fh.setFormatter(fmt)

        logger.addHandler(fh)

    return logger


def to_unicode(txt, encoding='utf8', errors='strict'):
    """Convert text to unicode.

    Args:
        txt:
        encoding:
        errors:

    Returns:
        str

    """
    if sys.version_info[0] >= 3:
        unicode = str

    if isinstance(txt, unicode):
        return txt
    return unicode(txt, encoding, errors=errors)
