import os
from typing import List, Generator, Set
from FEV_KEGG.settings import cachePath

import pickle
from FEV_KEGG.Util import Parallelism
import contextlib
import tempfile


def createPath(fileName):
    """
    Extracts the path from fileName and ensures all folders exist.
    """
    os.makedirs(os.path.dirname(os.path.join(cachePath, fileName)), exist_ok=True)

def writeToFile(content: 'will be encoded in UTF-8', fileName: 'will be overwritten, if already present', atomic = True):
    """
    tries to encode content into UTF-8 and save it to a file. Raises an error if encoding or saving fails.
    If 'atomic' == True, write file atomically.
    """
    createPath(fileName)
    path = os.path.join(cachePath, fileName)
    if atomic:
        with atomic_write(path, text = True) as file:
            file.write(content)
    else:
        with open(path, 'w', encoding = 'utf_8', errors = 'strict') as file:
            file.write(content)

def writeToFileBytes(data, fileName: 'will be overwritten, if already present', atomic = True):
    """
    If 'atomic' == True, write file atomically.
    """
    createPath(fileName)
    path = os.path.join(cachePath, fileName)
    if atomic:
        with atomic_write(path, text = False) as file:
            file.write(data)
    else:
        with open(path, 'wb') as file:
            file.write(data)

def readStringFromFileAtOnce(fileName) -> str:
    """
    returns a string from reading a file fully at once (more memory intensive) and decode content from UTF-8. Raises an error if reading or decoding fails.
    """
    with open(os.path.join(cachePath, fileName), 'r', encoding = 'utf_8', errors = 'strict') as file:
        
        string = ''.join([line for line in file])
        return string

def readBytesFromFileAtOnce(fileName):
    with open(os.path.join(cachePath, fileName), 'rb') as file:
        return file.read()

def readListFromFileAtOnce(fileName) -> List[str]:
    """
    returns a list of strings from reading a file fully at once (more memory intensive) and decode content from UTF-8. Raises an error if reading or decoding fails. Does NOT return the newline characters.
    """
    with open(os.path.join(cachePath, fileName), 'r', encoding = 'utf_8', errors = 'strict') as file:
        outputList = []
        for line in file:
            outputList.append(line.rstrip())
        return outputList
    
    
def readSetFromFileAtOnce(fileName) -> Set[str]:
    """
    returns a set of strings from reading a file fully at once (more memory intensive) and decode content from UTF-8. Raises an error if reading or decoding fails. Does NOT return the newline characters.
    """
    with open(os.path.join(cachePath, fileName), 'r', encoding = 'utf_8', errors = 'strict') as file:
        outputList = set()
        for line in file:
            outputList.add(line.rstrip())
        return outputList
    

def readGeneratorFromFileLinewise(fileName) -> Generator[str, None, None]:
    """
    returns a generator (can only be read once!) for reading a file line by line (less memory intensive), decoded from UTF-8. Raises an error if reading or decoding fails. Does NOT return the newline characters.
    """
    with open(os.path.join(cachePath, fileName), 'r', encoding = 'utf_8', errors = 'strict') as file:
        for line in file:
            yield line.rstrip()


def doesFileExist(fileName):
    """
    returns true if a file exists, false if not.
    """
    return os.path.isfile(os.path.join(cachePath, fileName))

def doesFolderExist(folderName):
    """
    returns True if a folder exists, False if not.
    """
    return os.path.isdir(os.path.join(cachePath, folderName))


def getFileHandleRead(fileName):
    """
    returns a handle to a read-only file
    """
    return open(os.path.join(cachePath, fileName), 'r', encoding = 'utf_8', errors = 'strict')


def getFileHandleWrite(fileName):
    """
    returns a handle to a write-only file
    """
    return open(os.path.join(cachePath, fileName), 'w', encoding = 'utf_8', errors = 'strict')







def cache(folder_path, file_name):
    """
    Checks if result of wrapped function has already been cached into the file specified by <cache directory>/'folder_path'/'file_name'. <cache directory> can be changed in settings.py
    If yes, read file and return content.
    If no, execute wrapped function, write result to file, and return result.
    """
    def decorator(func):
        
        def caching(*args):

            relativePath = os.path.join(folder_path, file_name)
            fullPath = os.path.join(cachePath, relativePath)
            
            if doesFileExist(relativePath) is True:
                with open(fullPath, 'rb') as file:
                    try:
                        content = pickle.load(file)
                    except Exception:
                        print("\n File causing the exception: " + fullPath + "\n")
                        raise
                return content
            else:
                
                createPath(fullPath) # create folders in path
                result = func(*args)
                with open(fullPath, 'wb') as file:
                    pickle.dump(result, file, protocol = pickle.HIGHEST_PROTOCOL)
                return result

        return caching

    return decorator

class CacheEntry(object):
    def __init__(self, isCached: bool, absolutePath: str, result = None):
        self.isCached = isCached
        self.absolutePath = absolutePath
        self.result = result
        
    def _readFile(self):
        with open(self.absolutePath, 'rb') as file:
            content = pickle.load(file) 
        return content
    
    def _writeFile(self):
        createPath(self.absolutePath) # create folders in path
        with open(self.absolutePath, 'wb') as file:
            pickle.dump(self.result, file, protocol = pickle.HIGHEST_PROTOCOL)
    
    def getResult(self, noDiskIO=False):
        """
        Automatically performs read or write operation in this thread.
        Unless 'noDiskIO' == True, then the result currently available in memory is returned. If the result had already been cached, this is most likely None!
        """
        if Parallelism.getShallCancelThreads() is True:
            import concurrent.futures
            raise concurrent.futures.CancelledError()
        
        if noDiskIO is True: # shall not perform disk I/O
            return self.result
        
        elif self.isCached is True: # result is in cache
            return self._readFile()
        
        else: # result is not in cache
            self._writeFile()
            return self.result

def cacheEntry(folder_path, file_name):
    """
    Similar to cache decorator, but does not read content from file nor write result to file.
    Instead, return a CacheEntry object. This object provides all information and methods necessary to read/write the desired data from cache.
    This is especially handy when splitting computation (in this function) from disk I/O (in CacheEntry) in a parallel computation environment.
    """
    def decorator(func):
        
        def caching(*args):

            relativePath = os.path.join(folder_path, file_name)
            fullPath = os.path.join(cachePath, relativePath)
               
            if doesFileExist(relativePath) is True:
                return CacheEntry(isCached=True, absolutePath=fullPath)
            
            else:
                result = func(*args)
                return CacheEntry(isCached=False, absolutePath=fullPath, result=result)

        return caching

    return decorator

@contextlib.contextmanager
def atomic_write(filename, text=True, keep=False,
                 suffix='.bak', prefix='tmp'):
    """Context manager for overwriting a file atomically.
    Usage:
    >>> with atomic_write("myfile.txt") as f:  # doctest: +SKIP
    ...     f.write("data")
    The context manager opens a temporary file for writing in the same
    directory as `filename`. On cleanly exiting the with-block, the temp
    file is renamed to the given filename. If the original file already
    exists, it will be overwritten and any existing contents replaced.
    (On POSIX systems, the rename is atomic. Other operating systems may
    not support atomic renames, in which case the function name is
    misleading.)
    If an uncaught exception occurs inside the with-block, the original
    file is left untouched. By default the temporary file is not
    preserved. To keep the temp file, pass `keep=True`. Any errors in 
    deleting the temp file are ignored.
    By default, the temp file is opened in text mode. To use binary mode,
    pass `text=False` as an argument. On some operating systems, this make
    no difference.
    By default, the temp file will have a name starting with "tmp" and
    ending with ".bak". You can vary that by passing strings as the
    `suffix` and `prefix` arguments.
    """
    # Copyright (c) 2017 ActiveState Software Inc.
    # 
    # Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    # 
    # The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    # 
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

    path = os.path.dirname(filename)
    fd, tmp = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=path, text=text)
    replace = os.replace  # Python 3.3 and better.
    
    try:
        if text is True:
            with os.fdopen(fd, 'w', encoding = 'utf_8', errors = 'strict') as f:
                yield f
        else:
            with os.fdopen(fd, 'wb') as f:
                yield f
        # Perform an atomic rename (if possible). This will be atomic on 
        # POSIX systems, and Windows for Python 3.3 or higher.
        replace(tmp, filename)
        tmp = None

    finally:
        if (tmp is not None) and (not keep):
            # Silently delete the temporary file. Ignore any errors.
            try:
                os.unlink(tmp)
            except:
                pass
