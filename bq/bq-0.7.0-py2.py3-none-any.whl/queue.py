
import os, sys, subprocess, time, traceback, random, tempfile, logging
from glob import glob

from bl.dict import Dict
from bl.text import Text

LOG = logging.getLogger(__name__)

"""This queue library implements a simple file-based queue that is processed at 
set intervals by the queue process. JSON is the default queue entry data extension, 
processed according to the specs of the subclass. Queue entry data is passed to 
the process_entry() method as bytes. If there is one queue process, it is a 
synchronous queue -- entries are processed FIFO. If there are multiple queue 
processes, it is asynchronous -- each process is synchronous, but there is no 
synchronization between the processes; each process picks up the next entry.
"""

class Queue(Dict):

    def __init__(self, path, ingpath=None, outpath=None, errpath=None, **args):
        """
        path [REQ'D]    = the filesystem path to the queue directory. Created if it doesn't exist.
        ingpath         = the 'processing' directory, defaults to path+"/ING".
        outpath         = the 'finished' directory, defaults to path+"/OUT".
        errpath         = the 'error' directory, defaults to path+'/ERR'.
        **args          = any other arguments you want to define for your queue class.
        """
        if not os.path.exists(path): os.makedirs(path)
        if ingpath is None: ingpath = path + '/ING'
        if not os.path.exists(ingpath): os.makedirs(ingpath)
        if outpath is None: outpath = path + '/OUT'
        if not os.path.exists(outpath): os.makedirs(outpath)
        if errpath is None: errpath = path + '/ERR'
        if not os.path.exists(errpath): os.makedirs(errpath)
        Dict.__init__(self, path=path, ingpath=ingpath, outpath=outpath, errpath=errpath, **args)

    def __repr__(self):
        return "%s(path='%s')" % (self.__class__.__name__, self.path)

    def timestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S %Z")

    def listen(self, sleep=5):
        """listen to the queue directory, with a wait time in seconds between processing"""
        while True:
            self.process_queue()
            time.sleep(sleep)

    def insert(self, text, prefix="", suffix="", ext='.txt', duplicate=False):
        """insert the given queue entry into the queue.
        text    = the text of the queue entry (REQUIRED)
        prefix  = a prefix for each queue entry filename (default '')
        suffix  = a suffix for each queue entry filename (before extension, default '')
        ext     = the extension of the queue entry filename (default '.json') 
        """
        # only insert the entry if there is no other entry containing the same data
        # -- no need to duplicate an existing entry.
        if duplicate==False:
            qfns = self.list()
            for qfn in qfns:
                try:
                    with open(qfn, 'rb') as f:
                        qft = f.read().decode('utf-8')
                        if qft == text:
                            return qfn
                except:
                    # queue managed to get to the file before we read it -- no need to keep reading,
                    # since they are processed in the same order by self.list()
                    break
        qfn = os.path.join(self.path, "%s%s-%.5f%s%s" 
            % (prefix, time.strftime("%Y%m%d.%H%M%S"), random.random(), suffix, ext))
        qf = Text(fn=qfn, text=text)
        qf.write()
        return qfn

    def list(self, pattern="*"):
        """get a list of files currently in the queue, sorted in order."""
        return sorted([fn for fn in glob(os.path.join(self.path, pattern))
                if os.path.isfile(fn)])

    def index(self, qfn):
        """return the index of fn in the queue"""
        qfns = self.list()
        if qfn in qfns:
            return qfns.index(qfn)

    def process_queue(self):
        """Loop through all the currently-available queue entry files, in order; 
        For each file, 
            + read it, delete it (to prevent another process from reading), then process it
            + if an exception happens processing an entry, log it and continue to the next item
        """
        fns = self.list()
        for fn in fns:
            
            # ensure that another queue process has not and will not process this entry.
            try:
                ingfn = os.path.join(self.ingpath, os.path.basename(fn))
                os.rename(fn, ingfn)
            except:
                # assume that this queue entry has already been taken
                continue

            # process this entry
            try:
                self.process_entry(ingfn)
                outfn = os.path.join(self.outpath, os.path.basename(fn))
                os.rename(ingfn, outfn)
            except:
                self.handle_exception(fn=ingfn)

    def process_entry(self, fn):
        """override this method to define how your subclass queue processes entries.
        fn      : the filename of the queue entry, which is probably in self.outpath
        """

    def handle_exception(self, fn=None, **args):
        """Handle exceptions that occur during queue script execution.
        (Override this method to implement your own exception handling.)
        fn          = the filename of the queue entry.
        exception   = the exception object
        """
        if fn is not None and os.path.exists(fn):
            errfn = os.path.join(self.errpath, os.path.basename(fn))
            os.rename(fn, errfn)
            LOG.error("== EXCEPTION: %r %r" % (errfn, args))
            LOG.error(traceback.format_exc())
