 #!/usr/bin/env python

import os
import re
import math
import compileall
import zipfile
from glob import glob
from string import Formatter  # For Formatter().parse
from . import GPI, logger
from . import Utils, ConfigUtils, IOUtils, ColorPrimer
from .Decorators import ijob_handler
from PythonCK.ioutils import size
from PythonCK.ioutils import humansize as _humansize

#===============================================================================

def build_zippackage(pkgpath, dest='../_build'):
  """
  Given a full path to package, this method will build .pyc files and wrap
  into single zip file, useful for running private python lib on Dirac.

  Args:
    pkgpath (str): Full path to package dir (one with __init__).
    dest (str): Destination where the output zip should go. If None, this will make `_build` directory alongside the `pkgpath`.

  Return:
    string as path to product zip file.

  ## IF done correctly, it should be able to use as lib
  >>> tmpdir = getfixture('tmpdir')
  >>> import PythonCK
  >>> uri = os.path.split(PythonCK.__file__)[0]
  >>> _ = build_zippackage(uri, tmpdir)
  >>> os.path.exists(str(tmpdir.join('PythonCK.zip')))
  True

  """
  ## Prepare vars
  pkgpath      = os.path.expandvars(str(pkgpath))
  head,pkgname = os.path.split(pkgpath.rstrip('/'))
  outdir       = os.path.abspath(os.path.join(head, str(dest)))
  output       = os.path.join(outdir, pkgname+'.zip')

  ## Prepare env
  if os.path.exists(output):
    os.remove(output)
  if not os.path.exists(outdir):
    os.makedirs(outdir)

  # Recompile all *.pyc first
  compileall.compile_dir(pkgpath, quiet=True)

  # Walk though dircetory, collect all .pyc files
  with zipfile.ZipFile(output, 'w') as zipf:
    # Use os.walk instead of glob to preserve fullpath
    for root, dirs, files in os.walk(pkgpath):
      for fname in files:
        if fname.endswith('.pyc'):
          # Take path only from python/ onward
          fullpath = os.path.join(root,fname)
          zipf.write(fullpath, arcname=fullpath.replace(head, ''))
  return output

#===============================================================================

def job_attach_mylib(job):
  """
  Attach the zipfile of latest PythonCK+BenderCK to the inputsandbox

  Usage:

  >> j = Job()
  >> j.attach_mylib()

  but also don't forget this line in Bender as well

      import os, sys
      sys.path.append(os.path.join(os.getcwd(),'BenderCK.zip'))

  """

  pkgs = (
    '$HOME/mylib/PythonCK/python/PythonCK',
    '$HOME/mylib/BenderCK/python/BenderCK',
  )

  # if not hasattr(job.backend, 'inputSandboxLFNs'):
  #   logger.info('Ignore attach_mylib. Non-Dirac backend')
  #   return
  # is_grid = isinstance( job.backend, GPI.Dirac )
  vmajor  = re.findall( r'GANGA_(v\d+)', str(GPI))[0]

  ## Attaching the local lib one-by-one
  for pkgpath in pkgs:
    zipfilepath = build_zippackage(pkgpath)
    # if is_grid:
    #   filename  = os.path.split(zipfilepath)[-1]
    #   lfnpath   = IOUtils.lfn_abspath(filename)
    #   if not IOUtils.is_LFN_uptodate(zipfilepath, filename):
    #     IOUtils.lfn_put(zipfilepath)
    #   ## Prefix is needed (tiresomely) in inputSandboxLFNs
    #   if not lfnpath.startswith('LFN:'):
    #     lfnpath = 'LFN:'+lfnpath
    #   uri = lfnpath
    # else:
    #   uri = zipfilepath
    # job.backend.inputSandboxLFNs += [ lfnpath ]
    if vmajor=='v600':
      job.inputsandbox += [ zipfilepath ]  # 6.0
      logger.info("Attached to job.inputsandbox: " + zipfilepath)
    elif vmajor=='v601':
      job.inputfiles += [ zipfilepath ]  # 6.1
      logger.info("Attached to job.inputfiles: " + zipfilepath)
    else:
      raise ValueError('Unknown version: '+vmajor)
  ## finally, return self for possible chaining
  return job

def job_lfn_purge(job):
  """
  USE WITH CARE!
  Invoke this command to call DiracFile.remove all its remote LFN.

  If dry_run is True, parse all the queue but no actual removal.
  """
  # Prepare the deleting queue
  logger.info('Deleting queue: ')
  queue = []
  # for sj in job.subjobs:
  #   for fout in sj.outputfiles:
  #     lfn = getattr(fout, 'lfn', None)
  #     if isinstance(fout, DiracFile) and lfn:
  #       queue.append(fout)
  #       logger.info(fout.lfn)
  # Also from lfn_list
  for lfn in job.lfn_list():
    queue.append(GPI.DiracFile(lfn=lfn))
    logger.info(lfn)
  # Ask confirmation
  if 'Y' != raw_input('Remove all LFNs in subjobs of this job? IRREVERSIBLE! Y/[n]: '):
    logger.info('Aborted Job.lfn_purge')
    return
  # PROCEED!
  try:
    for fout in queue:
      GPI.queues.add(fout.remove)  # Use Ganga async
    keyword = ': LFN PURGED!'
    if not job.comment.endswith(keyword):
      job.comment += keyword
    logger.info('Total removed files: %r'%len(queue))
  except Exception as e:
    logger.warning(e)



@ijob_handler
def job_lfn_size(intjid, force_reload=False):
  """
  Given a job, try to read size of all its contents.
  Prefer the non-human readible version (let formatting to other interface).
  Cache-wise this is cheaper.
  """
  ## Retrieve list of the lfns
  list_lfn = job_lfn_list(intjid, force_reload)
  if not list_lfn:  # Final local, or non-final remote
    return None,None  # Return None to show that it doesn't exists

  raise NotImplementedError('DiracDMS.lfn_list moved...')

  # # Prefetch the latest catalogue from dirac-dms
  # raw_lfn_dat = DiracDMS.lfn_list(list_lfn, force_reload)
  # sum1 = 0  # Normal sum, no replica
  # sum2 = 0  # Replica sum (actual consumption)
  # for dat in raw_lfn_dat['Successful'].values():
  #   sum1 += dat['Size']
  #   sum2 += (dat['Size']*len(dat['Replicas']))
  # return sum1, sum2

@ijob_handler
def job_ppl_list(intjid, *args, **kwargs):
  """
  Return the list of all  __postprocesslocations__ found for this job,
  which can be the job's output or at subjob's output
  """
  wdir = ConfigUtils.dir_workspace(intjid)
  l1   = glob(os.path.join(wdir, 'output/__postprocesslocations__'))
  l2   = glob(os.path.join(wdir, '*/output/__postprocesslocations__'))
  return sorted(list(set(l1+l2)))

@ijob_handler
def job_lfn_list(intjid, **kwargs):
  """Given job id, loop over its output to get all lfn."""
  queue    = job_ppl_list( intjid, **kwargs )
  list_lfn = ( res for ppl in queue for res in IOUtils.extract_lfn_from_ppl(ppl))
  return sorted(list(set(list_lfn)))

@ijob_handler
def job_eos_list(intjid, **kwargs):
  queue    = job_ppl_list( intjid, **kwargs )
  list_eos = ( res for ppl in queue for res in IOUtils.extract_eos_from_ppl(ppl))
  return sorted(list(set(list_eos)))


@ijob_handler
def job_pfn_size(intjid, force_reload=False):
  """Return local disk comsumption of given jid."""
  # TODO: Not working properly because get_size also has its own caching decorator
  val1 = size(Utils.dir_workspace(intjid), force_reload=force_reload)
  val2 = size(Utils.dir_massstorage(intjid), force_reload=force_reload)
  return val1 + val2


#===============================================================================

def __format__(self, spec):
  """
  Enhancement at lower-level, for color-coordinated formatting.
  The color is consulted to ColorPrimer module.

  The spec is such that, given @field after the usual specification,
  the color-dependent will be added. The `field` need to be available
  from Job instance, as well as the rules defined in ColorPrimer.

  Method #1: Via format()
    format( job, '{name} -- {comment}' )

  Method #2: via str.format ( slightly more verbose to comply python2 )
    '{0.name} -- {0.comment}'.format( job )

  Algorithm
  - Iterate over master template's spec
    - For each subtemplate, get key, get respective value from Job
    - If key is request to be colorized,
      - Get respective colorizer from ColorPrimer
      - Find out which color is it from val
      - Get respective template, colorized it
    - Recombine subtemplate
    - call subtemplate.format

  Note: use `getattr( job, key )` to support attribute-request which is available
        in official GPI (whereas my OfflineGPI also have __getattr__ call.)

  >>> _ = getfixture('job197')
  >>> j = GPI.jobs(197)

  ## simple
  >>> format(j, '{name} -- {status}')
  'Z02MuMuLine -- completed'
  >>> '{0.name} -- {0.status}'.format(j)
  'Z02MuMuLine -- completed'

  ## object
  >>> format(j, '{application}')
  'Bender'

  ## nested
  >>> format(j, '{application.platform}')
  'x86_64-slc5-gcc46-opt'
  >>> format(j, '{application.events}')
  '-1'

  """
  res = ''
  for text,key,spec,conv in Formatter().parse(spec):
    ## Custom-access to the instance nested attribute
    try:
      value = eval('self.'+key)
    except KeyError:  # __getitem__ failed...
      # value = repr(e)
      value = '---'  # blank default

    ## Custom color, based on !spec
    if conv:
      colorizer = ColorPrimer.CONVERSION_PARAM[conv]
      cval = getattr(self, colorizer.__name__)  # Colorizer name is also Job's attr.
      temp = text + colorizer(cval).format('{:'+spec+'}')
    else:
      temp = '{}{{:{}}}'.format( text, spec )
    res += temp.format( value )
  return res

def __eq__(self, other):
  """Consider equality by their public attributes."""
  d1 = { key:val for key,val in vars(self).iteritems() if not key.startswith('_')}
  d2 = { key:val for key,val in vars(other).iteritems() if not key.startswith('_')}
  return d1==d2

#===============================================================================

class JobStruct(object):
  """
  Bare-bone struct used in quick construction, e.g., QuickOnlineJobtreeReader
  """
  def __format__(self, spec):
    return __format__(self, spec)

#   @property
#   def app(self):
#     return re.findall(r'<class name="(\S+)" .* category="applications">', self._dat)[0]

#   @property
#   def appchar(self):
#     """Return single-letter representation of self.app."""
#     return self._APPCHAR.get( self.app, '?' )

#   @property
#   def backend(self):
#     return re.findall(r'<class name="(\S+)" .* category="backends">', self._dat)[0]

@property
def is_final(self):
  """Return True if status is considered final."""
  return self.status in ('completed', 'failed', 'killed')

@property
def lensj(self):
  """
  Try to return number of subjobs in this job.
  """

  ## 1. lensj==0 for sure if there's no splitter!
  node = self.find('.//attribute[@name="splitter"]')
  if node is None:
    return 0

  ## 2. It's possible (in new scheme) to set this explicitly null
  ## if re.findall(r'<attribute name="splitter">\n\s+<value>None</value>', self._dat):
  value = node.find('value')
  if value is not None and eval(value.text) is None:
    return 0

  ## 3. The workspace output dir, if available, then largest int-subdir is it
  searchpath = ConfigUtils.dir_workspace(self.fqid)
  if os.path.exists(searchpath):
    l = [ int(s) for s in os.listdir(searchpath) if s.isdigit() ]
    if l and (max(l)==len(l)):  # Max value should also be the same as count
      return len(l)

  ## 4. Do educated guess from dat file
  spname = node.find('class').get('name')
  if spname == 'GaussSplitter':
    # return re.findall(r'numberOfJobs"> <value>(\d+)</value>', self._dat)[0]
    return int(node.find('.//attribute[@name="numberOfJobs"]').value)

  if spname == 'SplitByFiles':
    n1 = len(list(self.find('.//attribute[@name="files"]').find('sequence').findall('class')))
    n2 = int(node.find('.//attribute[@name="filesPerJob"]').find('value').text)
    return int(math.ceil(1.*n1/n2))

  logger.warning('Splitter-parser not yet implemented: %r'%spname)
  return None


@property
def humansize(self):
  if not self.is_final:
    return 'N/A'
  return _humansize(job_pfn_size(self.fqid))  # PFN only, for now...

_application_char = {
  'Bender'      : 'B',
  'Boole'       : 'L',
  'Brunel'      : 'R',
  'DaVinci'     : 'D',
  'Executable'  : 'X',
  'GaudiPython' : 'P',
  'Gauss'       : 'G',
  'Moore'       : 'M',
}
# For BasejobtreeReader
APP_LEGEND = 'APP    :  [B]ender, Boo[L]e, B[R]unel, [D]aVinci, E[X]ecutable, Gaudi[P]ython, [G]auss, [M]oore'

@property
def application_char(self):
  return _application_char[str(self.application)]
  # print _application_char.get( self.application, '?' )
  # return _application_char.get( self.application, '?' )


#   @property
#   def humantime(self):
#     if not self.is_final:
#       return 'N/A'
#     return Utils.strfdelta(self.time)

#   @property
#   def time(self):
#     return self._deltatime('final', 'new')


  # def _directfield(self, field):
  #   """
  #   Helper method to extract field from raw dat. Field name is appear the same
  #   as in the xml dat file.
  #   """
  #   try:
  #     s = re.findall(r'{}"> <value>\'(.*)\''.format(field), self._dat)[0]
  #     return s.replace('&gt;','>').replace('&amp;','&').replace('&lt;','<')
  #   except Exception, e:
  #     return 'ParsedError'

  # def _timefield(self, name):
  #   """
  #   Helper method to extract the time-based field. Eval raw string into datetime.
  #   """
  #   l = re.findall(r"'{}': (datetime.datetime\(.*?\))".format(name), self._dat)
  #   return eval(l[0]) if len(l)==1 else None

  # def _deltatime(self, tfinal, tinitial):
  #   """
  #   Helper method to calculate deltatime from given two timefield.
  #   """
  #   if not self._dat:
  #     return None
  #   tf = self._timefield(tfinal)
  #   ti = self._timefield(tinitial)
  #   return tf-ti if (tf and ti) else None


