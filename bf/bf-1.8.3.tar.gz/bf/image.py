
import logging
log = logging.getLogger(__name__)

import math, os, shutil, sys, subprocess
from bl.file import File

class Image(File):

    def im(self, cmd, quiet=True, **params):
        args = [cmd]
        if quiet==True:
            args += ['-quiet']
        for key in params.keys():
            args += ['-'+key]
            if str(params[key]) != "":
                args += [str(params[key])]
        args += [self.fn]
        log.debug("%r" % args)
        o = subprocess.check_output(args).decode('utf8')
        return o.strip()

    def gm(self, cmd, quiet=True, **params):
        _gm = os.environ.get('gm') or 'gm'
        args = [_gm, cmd]
        # if quiet not in [False, None]:
        #     args.append('-silent')
        for key in params.keys():
            args += ['-'+key]
            if str(params[key]) != "":
                args += [str(params[key])]
        args += [self.fn]
        log.debug("%r" % args)
        o = subprocess.check_output(args).decode('utf8')
        return o.strip()

    def mogrify(self, **params):
        return self.gm('mogrify', **params)

    def identify(self, **params):
        return self.gm('identify', **params)

    def convert(self, outfn=None, **params):
        if outfn is not None and File(fn=outfn).fn != self.fn:
            shutil.copy(self.fn, outfn)
        else:
            outfn = self.fn
        res = Image(fn=outfn).mogrify(**params)
        return outfn + ': ' + res
